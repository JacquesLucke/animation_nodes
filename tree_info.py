import bpy
from itertools import chain
from collections import defaultdict
from . utils.timing import measureTime
from . utils.handlers import eventHandler
from . preferences import forbidSubprogramRecursion
from . utils.nodes import getAnimationNodeTrees, iterAnimationNodesSockets, idToNode, idToSocket

# Global Node Data
###########################################

class NodeData:
    def __init__(self):
        self._reset()

    def _reset(self):
        self.nodes = []
        self.nodesByType = defaultdict(set)
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
        self.rerouteNodes = self.nodesByType["NodeReroute"]
        self.findLinksSkippingReroutes()

    def insertNodeTrees(self):
        for tree in getAnimationNodeTrees():
            self.insertNodes(tree.nodes)
            self.insertLinks(tree.links)

    def insertNodes(self, nodes):
        appendNode = self.nodes.append
        nodesByType = self.nodesByType
        typeByNode = self.typeByNode
        nodeByIdentifier = self.nodeByIdentifier
        socketsByNode = self.socketsByNode
        nodeBySocket = self.nodeBySocket
        reroutePairs = self.reroutePairs

        for node in nodes:
            nodeID = node.toID()
            inputIDs = [socket.toID() for socket in node.inputs]
            outputIDs = [socket.toID() for socket in node.outputs]

            appendNode(nodeID)
            typeByNode[nodeID] = node.bl_idname
            nodesByType[node.bl_idname].add(nodeID)
            nodeByIdentifier[getattr(node, "identifier", None)] = nodeID

            socketsByNode[nodeID] = (inputIDs, outputIDs)
            for socketID in chain(inputIDs, outputIDs):
                nodeBySocket[socketID] = nodeID

            if node.bl_idname == "NodeReroute":
                reroutePairs[inputIDs[0]] = outputIDs[0]
                reroutePairs[outputIDs[0]] = inputIDs[0]

    def insertLinks(self, links):
        linkedSocketsWithReroutes = self.linkedSocketsWithReroutes

        for link in links:
            originID = link.from_socket.toID()
            targetID = link.to_socket.toID()

            linkedSocketsWithReroutes[originID].append(targetID)
            linkedSocketsWithReroutes[targetID].append(originID)

    def findLinksSkippingReroutes(self):
        rerouteNodes = self.rerouteNodes
        nonRerouteNodes = filter(lambda n: n not in rerouteNodes, self.nodes)

        socketsByNode = self.socketsByNode
        linkedSockets = self.linkedSockets
        iterLinkedSockets = self.iterLinkedSockets
        chainIterable = chain.from_iterable

        for node in nonRerouteNodes:
            for socket in chainIterable(socketsByNode[node]):
                linkedSockets[socket] = tuple(iterLinkedSockets(socket))

    def iterLinkedSockets(self, socket):
        """If the socket is linked to a reroute node the function
        tries to find the next socket that is linked to the reroute"""
        for socket in self.linkedSocketsWithReroutes[socket]:
            if socket[0] in self.rerouteNodes:
                yield from self.iterLinkedSockets(self.reroutePairs[socket])
            else:
                yield socket



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
        self.nodeTreeName = nodeIDs[0][0]
        self.type = "Invalid"
        self.name = ""
        self.description = ""
        self.identifier = None
        self.analyse()

    def analyse(self):
        self.findSystemNodes()

        groupNodeAmount = self.groupInAmount + self.groupOutAmount
        loopNodeAmount = self.loopInAmount + self.generatorAmount + self.reassignParameterAmount + self.breakAmount

        self.type = "Invalid"

        if groupNodeAmount + loopNodeAmount + self.scriptAmount == 0:
            self.type = "Main"
        elif self.scriptAmount == 1:
            self.type = "Script"
        elif loopNodeAmount == 0:
            if self.groupInAmount == 0 and self.groupOutAmount == 1:
                self.identifier = self.groupOutputNode.groupInputIdentifier
                if self.identifier == "": self.identifier = None
            elif self.groupInAmount == 1 and self.groupOutAmount == 0:
                self.type = "Group"
            elif self.groupInAmount == 1 and self.groupOutAmount == 1:
                if idToNode(self.groupInputIDs[0]).identifier == idToNode(self.groupOutputIDs[0]).groupInputIdentifier:
                    self.type = "Group"
        elif groupNodeAmount == 0:
            possibleIdentifiers = list({idToNode(nodeID).loopInputIdentifier for nodeID in self.generatorOutputIDs + self.reassignParameterIDs + self.breakIDs})
            if self.loopInAmount == 0 and len(possibleIdentifiers) == 1:
                self.identifier = possibleIdentifiers[0]
            elif self.loopInAmount == 1 and len(possibleIdentifiers) == 0:
                self.type = "Loop"
            elif self.loopInAmount == 1 and len(possibleIdentifiers) == 1:
                if idToNode(self.loopInputIDs[0]).identifier == possibleIdentifiers[0]:
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
        self.breakIDs = []
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
            elif idName == "an_LoopBreakNode":
                self.breakIDs.append(nodeID)
            elif idName == "an_ScriptNode":
                self.scriptIDs.append(nodeID)
            elif idName == "an_InvokeSubprogramNode":
                self.invokeSubprogramIDs.append(nodeID)

        self.groupInAmount = len(self.groupInputIDs)
        self.groupOutAmount = len(self.groupOutputIDs)
        self.loopInAmount = len(self.loopInputIDs)
        self.generatorAmount = len(self.generatorOutputIDs)
        self.reassignParameterAmount = len(self.reassignParameterIDs)
        self.breakAmount = len(self.breakIDs)
        self.scriptAmount = len(self.scriptIDs)

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
        return [node for node in self.getNodes() if node.isAnimationNode]

    @property
    def treeName(self):
        return self.nodeIDs[0][0]

    @property
    def nodeTree(self):
        return bpy.data.node_groups[self.treeName]

    @property
    def isSubnetwork(self):
        return self.type in ("Group", "Loop", "Script")

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
    def breakNodes(self):
        return [idToNode(nodeID) for nodeID in self.breakIDs]

    @property
    def scriptNode(self):
        try: return idToNode(self.scriptIDs[0])
        except: return None

class SpecialNodesAndSockets:
    def __init__(self):
        self.reset()

    def reset(self):
        self.socketsThatNeedUpdate = set()

    def update(self):
        self.reset()
        socketsThatNeedUpdate = self.socketsThatNeedUpdate
        for socket in iterAnimationNodesSockets():
            if hasattr(socket, "updateProperty"):
                socketsThatNeedUpdate.add(socket.toID())


_data = NodeData()
_networks = NodeNetworks()
_specialNodesAndSockets = SpecialNodesAndSockets()
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

@eventHandler("FILE_LOAD_POST")
@measureTime
def update():
    _data.update()
    _networks.update()
    _specialNodesAndSockets.update()

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

def getIdentifierAmount():
    return len(_data.nodeByIdentifier)

@updateAndRetryOnException
def getNodesByType(idName):
    return [idToNode(nodeID) for nodeID in _data.nodesByType[idName]]


def isSocketLinked(socket):
    return len(_data.linkedSockets[socket.toID()]) > 0


def getDirectlyLinkedSockets(socket):
    socketID = socket.toID()
    linkedIDs = _data.linkedSocketsWithReroutes[socketID]
    return [idToSocket(linkedID) for linkedID in linkedIDs]

def getDirectlyLinkedSocket(socket):
    socketID = socket.toID()
    linkedSocketIDs = _data.linkedSocketsWithReroutes[socketID]
    if len(linkedSocketIDs) > 0:
        return idToSocket(linkedSocketIDs[0])


def getLinkedSockets(socket):
    socketID = socket.toID()
    linkedIDs = _data.linkedSockets[socketID]
    return [idToSocket(linkedID) for linkedID in linkedIDs]

def getLinkedSocket(socket):
    socketID = socket.toID()
    linkedIDs = _data.linkedSockets[socketID]
    if len(linkedIDs) > 0:
        return idToSocket(linkedIDs[0])

def iterSocketsThatNeedUpdate():
    for socketID in _specialNodesAndSockets.socketsThatNeedUpdate:
        yield idToSocket(socketID)


# improve performance of higher level functions

def getOriginNodes(node):
    nodeID = node.toID()
    linkedNodeIDs = set()
    for socketID in _data.socketsByNode[nodeID][0]:
        for linkedSocketID in _data.linkedSockets[socketID]:
            linkedNodeIDs.add(linkedSocketID[0])
    return [idToNode(nodeID) for nodeID in linkedNodeIDs]

def getAllDataLinks():
    dataLinks = set()
    for socketID, linkedIDs in _data.linkedSockets.items():
        for linkedID in linkedIDs:
            if not socketID[1]: socketID, linkedID = linkedID, socketID
            dataLinks.add((idToSocket(socketID), idToSocket(linkedID)))
    return list(dataLinks)


# keep node state

def keepNodeState(function):
    def wrapper(node, *args, **kwargs):
        return keepNodeLinks(keepSocketValues(function))(node, *args, **kwargs)
    return wrapper

# keep node links

def keepNodeLinks(function):
    def wrapper(node, *args, **kwargs):
        connections = getNodeConnections(node)
        output = function(node, *args, **kwargs)
        setConnections(connections)
        return output
    return wrapper

def getNodeConnections(node):
    nodeID = node.toID()
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

# keep socket values

def keepSocketValues(function):
    def wrapper(node, *args, **kwargs):
        inputs, outputs = getSocketValues(node)
        output = function(node, *args, **kwargs)
        setSocketValues(node, inputs, outputs)
        return output
    return wrapper

def getSocketValues(node):
    inputs = [getSocketData(socket) for socket in node.inputs]
    outputs = [getSocketData(socket) for socket in node.outputs]
    return inputs, outputs

def getSocketData(socket):
    return (socket.identifier, socket.dataType, socket.getProperty(), socket.hide, socket.isUsed)

def setSocketValues(node, inputs, outputs):
    inputsByIdentifier = node.inputsByIdentifier
    for identifier, dataType, value, hide, isUsed in inputs:
        if getattr(inputsByIdentifier.get(identifier), "dataType", "") == dataType:
            socket = inputsByIdentifier[identifier]
            socket.setProperty(value)
            socket.hide = hide
            socket.isUsed = isUsed

    outputsByIdentifier = node.outputsByIdentifier
    for identifier, dataType, value, hide, isUsed in outputs:
        if getattr(outputsByIdentifier.get(identifier), "dataType", "") == dataType:
            socket = outputsByIdentifier[identifier]
            socket.setProperty(value)
            socket.hide = hide
            socket.isUsed = isUsed


def getNetworkWithNode(node):
    return _networks.networkByNode[node.toID()]

def getNetworks():
    return _networks.networks

def getSubprogramNetworks():
    return [network for network in _networks.networks if network.isSubnetwork]

def getNetworksByType(type = "Main"):
    return [network for network in _networks.networks if network.type == type]

def getNetworkByIdentifier(identifier):
    for network in getNetworks():
        if network.identifier == identifier: return network
    return None

def getNetworksByNodeTree(nodeTree):
    return [network for network in getNetworks() if network.nodeTreeName == nodeTree.name]

def getSubprogramNetworksByNodeTree(nodeTree):
    return [network for network in _networks.networks if network.isSubnetwork and network.nodeTreeName == nodeTree.name]
