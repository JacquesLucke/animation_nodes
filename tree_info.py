import bpy
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
        self.networkByNode = {}

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

        for network in self.networks:
            for nodeID in network.nodeIDs:
                self.networkByNode[nodeID] = network

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
        self.analyse()

    def analyse(self):
        self.findSystemNodes()

        groupInAmount = len(self.groupInputIDs)
        groupOutAmount = len(self.groupOutputIDs)
        loopInAmount = len(self.loopInputIDs)
        generatorAmount = len(self.generatorOutputIDs)
        reassignParameterAmount = len(self.reassignParameterIDs)
        scriptAmount = len(self.scriptIDs)

        groupNodeAmount = groupInAmount + groupOutAmount
        loopNodeAmount = loopInAmount + generatorAmount + reassignParameterAmount

        self.type = "Invalid"

        if groupNodeAmount + loopNodeAmount + scriptAmount == 0:
            self.type = "Main"
        elif scriptAmount == 1:
            self.type = "Script"
        elif loopNodeAmount == 0:
            if groupInAmount == 0 and groupOutAmount == 1:
                self.identifier = self.groupOutputNode.groupInputIdentifier
            elif groupInAmount == 1 and groupOutAmount == 0:
                self.type = "Group"
            elif groupInAmount == 1 and groupOutAmount == 1:
                if idToNode(self.groupInputIDs[0]).identifier == idToNode(self.groupOutputIDs[0]).groupInputIdentifier:
                    self.type = "Group"
        elif groupNodeAmount == 0:
            possibleIdentifiers = list({idToNode(nodeID).loopInputIdentifier for nodeID in self.generatorOutputIDs + self.reassignParameterIDs})
            if loopInAmount == 0 and len(possibleIdentifiers) == 1:
                self.identifier = possibleIdentifiers[0]
            elif loopInAmount == 1 and len(possibleIdentifiers) == 0:
                self.type = "Loop"
            elif loopInAmount == 1 and len(possibleIdentifiers) == 1:
                if idToNode(loopInputs[0]).identifier == possibleIdentifiers[0]:
                    self.type = "Loop"

        if self.type == "Script": owner = self.scriptNode
        elif self.type == "Group": owner = self.groupInputNode
        elif self.type == "Loop": owner = self.loopInputNode

        if self.type in ("Group", "Loop", "Script"):
            self.identifier = owner.identifier
            self.name = owner.subprogramName
            self.description = owner.subprogramDescription

            if forbidSubprogramRecursion():
                if self.identifier in self.getInvokedSubprogramIdentifiers():
                    self.type = "Invalid"
                    from . import problems
                    problems.SubprogramInvokesItself(self).report()

    def findSystemNodes(self):
        self.groupInputIDs = []
        self.groupOutputIDs = []
        self.loopInputIDs = []
        self.generatorOutputIDs = []
        self.reassignParameterIDs = []
        self.scriptIDs = []
        self.invokeSubprogramIDs = []

        for nodeID in self.nodeIDs:
            idName = _data.typeByNode[nodeID]
            if idName == "an_GroupInputNode":
                self.groupInputIDs.append(nodeID)
            elif idName == "an_GroupOutputNode":
                self.groupOutputIDs.append(nodeID)
            elif idName == "an_LoopInputNode":
                self.loopInputIDs.append(nodeID)
            elif idName == "an_LoopGeneratorOutputNode":
                self.generatorOutputIDs.append(nodeID)
            elif idName == "an_ReassignLoopParameterNode":
                self.reassignParameterIDs.append(nodeID)
            elif idName == "an_ScriptNode":
                self.scriptIDs.append(nodeID)
            elif idName == "an_InvokeSubprogramNode":
                self.invokeSubprogramIDs.append(nodeID)

    def getInvokedSubprogramIdentifiers(self):
        return list({idToNode(nodeID).subprogramIdentifier for nodeID in self.invokeSubprogramIDs})

    @staticmethod
    def join(networks):
        nodeIDs = []
        for network in networks:
            nodeIDs.extend(network.nodeIDs)
        return NodeNetwork(nodeIDs)

    def getNodes(self):
        return [idToNode(nodeID) for nodeID in self.nodeIDs]

    def getAnimationNodes(self):
        return [node for node in self.getNodes() if hasattr(node, "isAnimationNode")]

    @property
    def treeName(self):
        return self.nodeIDs[0][0]

    @property
    def ownerNode(self):
        try: return getNodeByIdentifier(self.identifier)
        except: return None

    @property
    def groupInputNode(self):
        try: return idToNode(self.groupInputIDs[0])
        except: return None

    @property
    def groupOutputNode(self):
        try: return idToNode(self.groupOutputIDs[0])
        except: return None

    @property
    def loopInputNode(self):
        try: return idToNode(self.loopInputIDs[0])
        except: return None

    @property
    def generatorOutputNodes(self):
        return [idToNode(nodeID) for nodeID in self.generatorOutputIDs]

    @property
    def reassignParameterNodes(self):
        return [idToNode(nodeID) for nodeID in self.reassignParameterIDs]

    @property
    def scriptNode(self):
        try: return idToNode(self.scriptIDs[0])
        except: return None


_data = NodeData()
_networks = NodeNetworks()
_needsUpdate = True


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

    global _needsUpdate
    _needsUpdate = False

def updateIfNecessary():
    if _needsUpdate:
        update()

def treeChanged():
    global _needsUpdate
    _needsUpdate = True



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
    return _networks.networkByNode[nodeToID(node)]

def getNetworks():
    return _networks.networks

def getSubprogramNetworks():
    return [network for network in _networks.networks if network.type in ("Group", "Loop", "Script")]

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
