import bpy
from collections import defaultdict
from . utils.nodes import getAnimationNodeTrees, getNode, getSocket
from . utils.timing import measureTime

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


data = NodeData()



# Public API
##################################

@measureTime
def update():
    data.update()

def isSocketLinked(socket):
    socketID = socketToID(socket)
    return len(data.linkedSockets[socketID]) > 0




# Utilities
###################################

def socketToID(socket):
    return (nodeToID(socket.node), socket.is_output, socket.identifier)

def nodeToID(node):
    return (node.id_data.name, node.name)

def idToSocket(socketID):
    return getSocket(*socketID)

def idToNode(nodeID):
    return getNode(*nodeID)


class NodeNetwork:
    def __init__(self, nodeGroupInfo):
        self.info = nodeGroupInfo


class NodeGroupInfo:
    def __init__(self):
        self._reset()

    def _reset(self):
        self.nodesByType = defaultdict(list)
        self.typeByNode = defaultdict(None)
        self.linkedSockets = defaultdict(list)
        self.reroutePairs = defaultdict(list)
        self.socketsByNode = defaultdict(lambda: ([], []))
        self.nodeBySocket = defaultdict(None)
        self.linksByNode = defaultdict(list)

    def insertNodeTree(self, tree):
        self.insertBlenderNodes(tree.nodes)
        self.insertBlenderLinks(tree.links)

    def insertBlenderNodes(self, nodes):
        for node in nodes:
            nodeID = nodeToID(node)
            inputIDs = [socketToID(socket) for socket in node.inputs]
            outputIDs = [socketToID(socket) for socket in node.outputs]
            self.socketsByNode[nodeID] = (inputIDs, outputIDs)
            self.nodesByType[node.bl_idname].append(nodeID)
            self.typeByNode[nodeID] = node.bl_idname
            for socketID in inputIDs + outputIDs:
                self.nodeBySocket[socketID] = nodeID

            if node.bl_idname == "NodeReroute":
                inputID = socketToID(node.inputs[0])
                outputID = socketToID(node.outputs[0])
                self.reroutePairs[inputID] = outputID
                self.reroutePairs[outputID] = inputID

    def insertBlenderLinks(self, links):
        for link in links:
            if not link.is_valid: continue
            originID = socketToID(link.from_socket)
            targetID = socketToID(link.to_socket)
            linkID = (originID, targetID)
            self.linkedSockets[originID].append(targetID)
            self.linkedSockets[targetID].append(originID)
            self.linksByNode[originID[0]].append(linkID)
            self.linksByNode[targetID[0]].append(linkID)

    def getSeparatedGroups(self):
        groups = self.getLinkedGroups()
        return [self.infoFromNodes(group) for group in groups]

    def infoFromNodes(self, nodes):
        groupInfo = NodeGroupInfo()
        links = self.getLinksOfNodes(nodes)

        for node in nodes:
            type = self.typeByNode[node]
            groupInfo.nodesByType[type].append(node)
            groupInfo.typeByNode[node] = self.typeByNode[node]
            inputs, outputs = self.socketsByNode[node]
            groupInfo.socketsByNode[node] = (inputs, outputs)
            for socket in inputs + outputs:
                groupInfo.nodeBySocket[socket] = node

        for link in links:
            origin, target = link
            groupInfo.linkedSockets[origin] = target
            groupInfo.linkedSockets[target] = origin
            inputNode = self.nodeBySocket[origin]
            outputNode = self.nodeBySocket[target]
            groupInfo.linksByNode[inputNode] = link
            groupInfo.linksByNode[outputNode] = link

        return groupInfo

    def getLinksOfNodes(self, nodes):
        links = set()
        for node in nodes:
            links.update(self.linksByNode[node])
        return list(links)

    def getLinkedGroups(self):
        groups = []
        unassignedNodes = set(self.nodes)
        while len(unassignedNodes) > 0:
            node = unassignedNodes.pop()
            linkedNodes = self.getLinkedNodes(node)
            groups.append(linkedNodes)
            unassignedNodes -= set(linkedNodes)
        return groups

    def getLinkedNodes(self, node):
        linkedNodes = set()
        nodesToCheck = {node}
        while len(nodesToCheck) > 0:
            node = nodesToCheck.pop()
            linkedNodes.add(node)
            directlyLinkedNodes = self.getDirectlyLinkedNodes(node)
            for node in directlyLinkedNodes:
                if node not in linkedNodes: nodesToCheck.add(node)
        return list(linkedNodes)

    def getDirectlyLinkedNodes(self, node):
        return self.getDirectParentNodes(node) + self.getDirectChildNodes(node)

    def getDirectParentNodes(self, node):
        return self.getLinkedNodesFromSockets(self.socketsByNode[node][0])

    def getDirectChildNodes(self, node):
        return self.getLinkedNodesFromSockets(self.socketsByNode[node][1])

    def getLinkedNodesFromSockets(self, nodeSockets):
        linkedSockets = set()
        for inputSocket in nodeSockets:
            sockets = [socket for socket in self.getLinkedSockets(inputSocket)]
            linkedSockets.update(sockets)

        connectedNodes = set()
        for socket in linkedSockets:
            connectedNodes.add(self.nodeBySocket[socket])
        return list(connectedNodes)

    def getLinkedSockets(self, socket):
        """If the socket is linked to a reroute node the function
        tries to find the next socket that is linked to the reroute"""
        linkedSockets = []
        for socket in self.linkedSockets[socket]:
            if self.isRerouteSocket(socket):
                rerouteInputSocket = self.reroutePairs[socket]
                sockets = self.getLinkedSockets(rerouteInputSocket)
                linkedSockets.extend(sockets)
            else:
                linkedSockets.append(socket)
        return linkedSockets


    @property
    def nodes(self):
        """Reroute and Frame nodes don't count as regular nodes"""
        allNodes = []
        for type, nodes in self.nodesByType.items():
            if type in ("NodeReroute", "NodeFrame"): continue
            allNodes.extend(nodes)
        return allNodes

    def isRerouteSocket(self, id):
        return self.isRerouteNode(id[0])

    def isRerouteNode(self, id):
        return id in self.nodesByType["NodeReroute"]


class TestTreeInfo(bpy.types.Operator):
    bl_idname = "an.test_tree_info"
    bl_label = "Test Tree Info"

    def execute(self, context):
        import time
        groups = test()
        return {"FINISHED"}

@measureTime
def test():
    info = NodeGroupInfo()
    info.insertNodeTree(bpy.data.node_groups[0])
    groups = info.getSeparatedGroups()
    return groups

from pprint import PrettyPrinter
def pprint(data):
    pp = PrettyPrinter()
    pp.pprint(data)
