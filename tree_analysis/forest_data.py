from itertools import chain
from collections import defaultdict
from .. utils.nodes import getAnimationNodeTrees

class ForestData:
    def __init__(self):
        self._reset()

    def _reset(self):
        self.nodes = []
        self.nodesByType = defaultdict(set)
        self.typeByNode = defaultdict(None)
        self.nodeByIdentifier = defaultdict(None)

        self.socketsByNode = defaultdict(lambda: ([], []))

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
                linkedSockets[socket] = tuple(iterLinkedSockets(socket, set()))

    def iterLinkedSockets(self, socket, visitedReroutes):
        """If the socket is linked to a reroute node the function
        tries to find the next socket that is linked to the reroute"""
        for socket in self.linkedSocketsWithReroutes[socket]:
            if socket[0] in self.rerouteNodes:
                if socket[0] in visitedReroutes:
                    print("Reroute recursion detected in: {}".format(repr(socket[0][0])))
                    return
                visitedReroutes.add(socket[0])
                yield from self.iterLinkedSockets(self.reroutePairs[socket], visitedReroutes)
            else:
                yield socket
