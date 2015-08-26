import bpy
from . import problems
from collections import defaultdict
from . utils.timing import measureTime
from bpy.app.handlers import persistent
from . preferences import forbidSubprogramRecursion
from . utils.nodes import getAnimationNodeTrees, getNode, getSocket

# Global Node Data
###########################################

class NodeData:
    def __init__(self):
        self._reset()

    def _reset(self):
        self.nodes = []
        self.nodesByType = defaultdict(list)
        self.typeByNode = defaultdict(None)
        self.nodeByIdentifier = defaultdict(None)

        self.socketsByNode = defaultdict(lambda: ([], []))
        self.nodeBySocket = defaultdict(None)

        self.linkedSockets = defaultdict(list)
        self.linkedSocketsWithReroutes = defaultdict(list)
        self.reroutePairs = defaultdict(list)

    def update(self):
        self._reset()
        self.insertNodeTrees()
        self.findLinksSkippingReroutes()

    def insertNodeTrees(self):
        for tree in getAnimationNodeTrees():
            self.insertNodes(tree.nodes)
            self.insertLinks(tree.links)

    def insertNodes(self, nodes):
        for node in nodes:
            nodeID = nodeToID(node)
            inputIDs = [socketToID(socket) for socket in node.inputs]
            outputIDs = [socketToID(socket) for socket in node.outputs]

            self.nodes.append(nodeID)
            self.nodesByType[node.bl_idname].append(nodeID)
            self.typeByNode[nodeID] = node.bl_idname
            self.nodeByIdentifier[getattr(node, "identifier", None)] = nodeID

            self.socketsByNode[nodeID] = (inputIDs, outputIDs)
            for socketID in inputIDs + outputIDs:
                self.nodeBySocket[socketID] = nodeID

            if node.bl_idname == "NodeReroute":
                inputID = socketToID(node.inputs[0])
                outputID = socketToID(node.outputs[0])
                self.reroutePairs[inputID] = outputID
                self.reroutePairs[outputID] = inputID

    def insertLinks(self, links):
        for link in links:
            originID = socketToID(link.from_socket)
            targetID = socketToID(link.to_socket)
            linkID = (originID, targetID)

            self.linkedSocketsWithReroutes[originID].append(targetID)
            self.linkedSocketsWithReroutes[targetID].append(originID)

    def findLinksSkippingReroutes(self):
        for node in self.nodes:
            if self.isRerouteNode(node): continue
            inputs, outputs = self.socketsByNode[node]
            for socket in inputs + outputs:
                linkedSockets = self.getLinkedSockets(socket)
                self.linkedSockets[socket] = linkedSockets

    def getLinkedSockets(self, socket):
        """If the socket is linked to a reroute node the function
        tries to find the next socket that is linked to the reroute"""
        linkedSockets = []
        for socket in self.linkedSocketsWithReroutes[socket]:
            if self.isRerouteSocket(socket):
                rerouteInputSocket = self.reroutePairs[socket]
                sockets = self.getLinkedSockets(rerouteInputSocket)
                linkedSockets.extend(sockets)
            else:
                linkedSockets.append(socket)
        return linkedSockets

    def isRerouteSocket(self, id):
        return self.isRerouteNode(id[0])

    def isRerouteNode(self, id):
        return id in self.nodesByType["NodeReroute"]

class NodeNetworks:
    def __init__(self):
        self._reset()

    def _reset(self):
        self.networks = []

    def getNetworkWithNode(self, node):
        for network in self.networks:
            if network.contains(node): return network

    def update(self):
        self._reset()

        nodeGroups = self.getNodeGroups()

        networksByIdentifier = defaultdict(list)
        for nodes in nodeGroups:
            if not self.groupContainsAnimationNodes(nodes): continue
            network = NodeNetwork(nodes)
            networksByIdentifier[network.identifier].append(network)

        for identifier, networks in networksByIdentifier.items():
            if identifier is None: self.networks.extend(networks)
            else: self.networks.append(NodeNetwork.join(networks))

    def groupContainsAnimationNodes(self, nodes):
        for node in nodes:
            if _data.typeByNode[node] not in ("NodeFrame", "NodeReroute"): return True
        return False

    def getNodeGroups(self):
        groups = []
        foundNodes = set()
        for node in _data.nodes:
            if node not in foundNodes:
                nodeGroup = self.getAllConnectedNodes(node)
                foundNodes.update(nodeGroup)
                groups.append(nodeGroup)
        return groups

    def getAllConnectedNodes(self, nodeInGroup):
        connectedNodes = set()
        uncheckedNodes = {nodeInGroup}
        while len(uncheckedNodes) > 0:
            node = uncheckedNodes.pop()
            connectedNodes.add(node)
            linkedNodes = self.getDirectlyLinkedNodes(node)
            for linkedNode in linkedNodes:
                if linkedNode not in uncheckedNodes and linkedNode not in connectedNodes:
                    uncheckedNodes.add(linkedNode)
        return list(connectedNodes)

    def getDirectlyLinkedNodes(self, node):
        nodes = set()
        inputs, outputs = _data.socketsByNode[node]
        for socket in inputs + outputs:
            for linkedSocket in _data.linkedSocketsWithReroutes[socket]:
                nodes.add(linkedSocket[0])
        return nodes


class NodeNetwork:
    def __init__(self, nodeIDs):
        self.nodeIDs = nodeIDs
        self.type = "Invalid"
        self.name = ""
        self.description = ""
        self.identifier = None
        self.groupInputID = None
        self.groupOutputID = None
        self.generatorOutputIDs = []
        self.analyse()

    def analyse(self):
        groupInputs = []
        groupOutputs = []
        loopInputs = []
        generatorOutputs = []
        invokedIdentifiers = set()

        for nodeID in self.nodeIDs:
            idName = _data.typeByNode[nodeID]
            if idName == "an_GroupInputNode":
                groupInputs.append(nodeID)
            elif idName == "an_GroupOutputNode":
                groupOutputs.append(nodeID)
            elif idName == "an_LoopInputNode":
                loopInputs.append(nodeID)
            elif idName == "an_LoopGeneratorOutputNode":
                generatorOutputs.append(nodeID)
            elif idName == "an_InvokeSubprogramNode":
                invokedIdentifiers.add(idToNode(nodeID).subprogramIdentifier)

        groupInAmount = len(groupInputs)
        groupOutAmount = len(groupOutputs)
        loopInAmount = len(loopInputs)
        generatorAmount = len(generatorOutputs)

        self.type = "Invalid"

        if groupInAmount + groupOutAmount + loopInAmount + generatorAmount == 0:
            self.type = "Main"
        elif loopInAmount + generatorAmount == 0:
            if groupInAmount == 0 and groupOutAmount == 1:
                self.identifier = idToNode(groupOutputs[0]).groupInputIdentifier
            elif groupInAmount == 1 and groupOutAmount == 0:
                self.type = "Group"
            elif groupInAmount == 1 and groupOutAmount == 1:
                if idToNode(groupInputs[0]).identifier == idToNode(groupOutputs[0]).groupInputIdentifier:
                    self.type = "Group"
                    self.groupOutputID = groupOutputs[0]
        elif groupInAmount + groupOutAmount == 0:
            generatorOwners = list({idToNode(nodeID).loopInputIdentifier for nodeID in generatorOutputs})
            if loopInAmount == 0 and len(generatorOwners) == 1:
                self.identifier = generatorOwners[0]
            elif loopInAmount == 1 and len(generatorOwners) == 0:
                self.type = "Loop"
            elif loopInAmount == 1 and len(generatorOwners) == 1:
                if idToNode(loopInputs[0]).identifier == generatorOwners[0]:
                    self.type = "Loop"

        if self.type == "Group":
            owner = idToNode(groupInputs[0])
            self.groupInputID = groupInputs[0]

        if self.type == "Loop":
            owner = idToNode(loopInputs[0])
            self.loopInputID = loopInputs[0]
            self.generatorOutputIDs = generatorOutputs

        if self.type in ("Group", "Loop"):
            self.identifier = owner.identifier
            self.name = owner.subprogramName
            self.description = owner.subprogramDescription

            if forbidSubprogramRecursion():
                if self.identifier in invokedIdentifiers:
                    self.type = "Invalid"
                    problems.report("{} invokes itself".format(repr(self.name)), forbidUnitCreation = True, forbidExecution = True)

    @staticmethod
    def join(networks):
        nodeIDs = []
        for network in networks:
            nodeIDs.extend(network.nodeIDs)
        return NodeNetwork(nodeIDs)

    def contains(self, nodeID):
        return nodeID in self.nodeIDs

    def getNodes(self):
        return [idToNode(nodeID) for nodeID in self.nodeIDs]

    def getAnimationNodes(self):
        return [node for node in self.getNodes() if hasattr(node, "isAnimationNode")]

    @property
    def treeName(self):
        return self.nodeIDs[0][0]

    @property
    def groupInputNode(self):
        if self.groupInputID is None: return None
        return idToNode(self.groupInputID)

    @property
    def groupOutputNode(self):
        if self.groupOutputID is None: return None
        return idToNode(self.groupOutputID)

    @property
    def loopInputNode(self):
        if self.loopInputID is None: return None
        return idToNode(self.loopInputID)

    @property
    def generatorOutputNodes(self):
        return [idToNode(nodeID) for nodeID in self.generatorOutputIDs]


_data = NodeData()
_networks = NodeNetworks()


def updateAndRetryOnException(function):
    def wrapper(*args, **kwargs):
        try:
            output = function(*args, **kwargs)
        except:
            update()
            output = function(*args, **kwargs)
        return output
    return wrapper


# Public API
##################################

@measureTime
def update():
    _data.update()
    _networks.update()


def getNodeByIdentifier(identifier):
    return idToNode(_data.nodeByIdentifier[identifier])

@updateAndRetryOnException
def getNodesByType(idName):
    return [idToNode(nodeID) for nodeID in _data.nodesByType[idName]]


def isSocketLinked(socket):
    socketID = socketToID(socket)
    return len(_data.linkedSockets[socketID]) > 0


def getDirectlyLinkedSockets(socket):
    socketID = socketToID(socket)
    linkedIDs = _data.linkedSocketsWithReroutes[socketID]
    return [idToSocket(linkedID) for linkedID in linkedIDs]

def getDirectlyLinkedSocket(socket):
    socketID = socketToID(socket)
    linkedSocketIDs = _data.linkedSocketsWithReroutes[socketID]
    if len(linkedSocketIDs) > 0:
        return idToSocket(linkedSocketIDs[0])


def getLinkedSockets(socket):
    socketID = socketToID(socket)
    linkedIDs = _data.linkedSockets[socketID]
    return [idToSocket(linkedID) for linkedID in linkedIDs]

def getLinkedSocket(socket):
    socketID = socketToID(socket)
    linkedIDs = _data.linkedSockets[socketID]
    if len(linkedIDs) > 0:
        return idToSocket(linkedIDs[0])


def getAllDataLinks():
    dataLinks = set()
    for socketID, linkedIDs in _data.linkedSockets.items():
        for linkedID in linkedIDs:
            if not socketID[1]: socketID, linkedID = linkedID, socketID
            dataLinks.add((idToSocket(socketID), idToSocket(linkedID)))
    return list(dataLinks)

def getNodeConnections(node):
    nodeID = nodeToID(node)
    inputIDs, outputIDs = _data.socketsByNode[nodeID]
    connections = []
    for socketID in inputIDs + outputIDs:
        for linkedID in _data.linkedSocketsWithReroutes[socketID]:
            connections.append((socketID, linkedID))
    return connections

def setConnections(connections):
    for id1, id2 in connections:
        try: idToSocket(id1).linkWith(idToSocket(id2))
        except: pass

def keepNodeLinks(function):
    def wrapper(node, *args, **kwargs):
        connections = getNodeConnections(node)
        output = function(node, *args, **kwargs)
        setConnections(connections)
        return output
    return wrapper

def getNetworkWithNode(node):
    return _networks.getNetworkWithNode(nodeToID(node))

def getNetworks():
    return _networks.networks

def getSubprogramNetworks():
    return [network for network in _networks.networks if network.type in ("Group", "Loop")]

def getNetworksByType(type = "Main"):
    return [network for network in _networks.networks if network.type == type]

def getNetworkByIdentifier(identifier):
    for network in getNetworks():
        if network.identifier == identifier: return network
    return None


# Utilities
###################################

def socketToID(socket):
    return (nodeToID(socket.node), socket.is_output, socket.identifier)

def nodeToID(node):
    return (node.id_data.name, node.name)

def idToSocket(socketID):
    return getSocket(socketID[0][0], socketID[0][1], socketID[1], socketID[2])

def idToNode(nodeID):
    return getNode(*nodeID)


from pprint import PrettyPrinter
def pprint(data):
    pp = PrettyPrinter()
    pp.pprint(data)



# Register
##################################

@persistent
def _updateTreeData(scene):
    update()

def registerHandlers():
    bpy.app.handlers.load_post.append(_updateTreeData)

def unregisterHandlers():
    bpy.app.handlers.load_post.remove(_updateTreeData)
