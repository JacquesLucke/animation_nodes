import bpy
from collections import defaultdict
from . utils.timing import measureTime
from bpy.app.handlers import persistent
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


_data = NodeData()



# Public API
##################################

@measureTime
def update():
    _data.update()

def isSocketLinked(socket):
    socketID = socketToID(socket)
    return len(_data.linkedSockets[socketID]) > 0

def getDirectOriginSocket(socket):
    socketID = socketToID(socket)
    linkedSockets = _data.linkedSocketsWithReroutes[socketID]
    if len(linkedSockets) > 0: return idToSocket(linkedSockets[0])

def getOriginSocket(socket):
    linkedSockets = getLinkedSockets(socket)
    if len(linkedSockets) > 0:
        return linkedSockets[0]

def getTargetSockets(socket):
    return getLinkedSockets(socket)

def getLinkedSockets(socket):
    socketID = socketToID(socket)
    return [idToSocket(linkedID) for linkedID in _data.linkedSockets[socketID]]

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
        socket1, socket2 = idToSocket(id1), idToSocket(id2)
        if socket1.is_output: socket1, socket2 = socket2, socket1
        tree = socket1.node.id_data
        tree.links.new(socket1, socket2)

def keepNodeLinks(function):
    def wrapper(node, *args, **kwargs):
        connections = getNodeConnections(node)
        output = function(node, *args, **kwargs)
        setConnections(connections)
        return output
    return wrapper




# Utilities
###################################

def socketToID(socket):
    return (nodeToID(socket.node), socket.is_output, socket.identifier)

def nodeToID(node):
    return (node.id_data.name, node.name)

def idToSocket(socketID):
    return getSocket(socketID[0][0], socketID[0][1], socketID[1], socketID[2])

def idToNode(nodeID):
    return getNode(nodeID)


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
