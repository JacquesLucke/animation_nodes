from ... node_creator import NodeCreator

class TransformsOutputLoop(NodeCreator):
    label = "Transforms Output Loop"

    def insert(self):
        activeNode = self.activeNode

        loopNode = self.newNode("an_LoopInputNode")
        objectIteratorSocket = loopNode.newIterator("Object List")
        transformsOutputNode = self.newNode("an_ObjectTransformsOutputNode", x = 500)
        objectIteratorSocket.linkWith(transformsOutputNode.inputs["Object"])

        activeListOutput = self.getObjectListOutput(activeNode)
        if activeListOutput is not None:
            invokeNode = self.newNode("an_InvokeSubprogramNode", move = False)
            invokeNode.location = activeNode.location
            invokeNode.location.x += 250
            invokeNode.subprogramIdentifier = loopNode.identifier
            activeListOutput.linkWith(invokeNode.inputs[0])

    def getObjectListOutput(self, node):
        for socket in node.outputs:
            if socket.dataType == "Object List": return socket
