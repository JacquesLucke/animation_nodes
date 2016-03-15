from . utils.timing import measureTime
from . utils.handlers import eventHandler
from . utils.nodes import iterAnimationNodesSockets, idToNode, idToSocket

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

def __setup():
    from . tree_analysis.forest_data import ForestData
    from . tree_analysis.networks import NodeNetworks

    _needsUpdate = True
    _forestData = ForestData()
    _networks = NodeNetworks()
    _specialNodesAndSockets = SpecialNodesAndSockets()

    global _needsUpdate, _forestData, _networks, _specialNodesAndSockets



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
    _forestData.update()
    _networks.update(_forestData)
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
    return idToNode(_forestData.nodeByIdentifier[identifier])

def getIdentifierAmount():
    return len(_forestData.nodeByIdentifier)

@updateAndRetryOnException
def getNodesByType(idName):
    return [idToNode(nodeID) for nodeID in _forestData.nodesByType[idName]]


def isSocketLinked(socket):
    return len(_forestData.linkedSockets[socket.toID()]) > 0


def getDirectlyLinkedSockets(socket):
    socketID = socket.toID()
    linkedIDs = _forestData.linkedSocketsWithReroutes[socketID]
    return [idToSocket(linkedID) for linkedID in linkedIDs]

def getDirectlyLinkedSocket(socket):
    socketID = socket.toID()
    linkedSocketIDs = _forestData.linkedSocketsWithReroutes[socketID]
    if len(linkedSocketIDs) > 0:
        return idToSocket(linkedSocketIDs[0])


def getLinkedSockets(socket):
    socketID = socket.toID()
    linkedIDs = _forestData.linkedSockets[socketID]
    return [idToSocket(linkedID) for linkedID in linkedIDs]

def getLinkedSocket(socket):
    socketID = socket.toID()
    linkedIDs = _forestData.linkedSockets[socketID]
    if len(linkedIDs) > 0:
        return idToSocket(linkedIDs[0])

def iterSocketsThatNeedUpdate():
    for socketID in _specialNodesAndSockets.socketsThatNeedUpdate:
        yield idToSocket(socketID)


# improve performance of higher level functions

def getOriginNodes(node):
    nodeID = node.toID()
    linkedNodeIDs = set()
    for socketID in _forestData.socketsByNode[nodeID][0]:
        for linkedSocketID in _forestData.linkedSockets[socketID]:
            linkedNodeIDs.add(linkedSocketID[0])
    return [idToNode(nodeID) for nodeID in linkedNodeIDs]

def getAllDataLinks():
    dataLinks = set()
    for socketID, linkedIDs in _forestData.linkedSockets.items():
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
    inputIDs, outputIDs = _forestData.socketsByNode[nodeID]
    connections = []
    for socketID in inputIDs + outputIDs:
        for linkedID in _forestData.linkedSocketsWithReroutes[socketID]:
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
    return [network for network in getNetworks() if network.treeName == nodeTree.name]

def getSubprogramNetworksByNodeTree(nodeTree):
    return [network for network in _networks.networks if network.isSubnetwork and network.treeName == nodeTree.name]

__setup()
