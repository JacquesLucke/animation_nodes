class SocketTemplate:
    def createAsInput(self, node):
        return self.create(node, node.inputs)

    def createAsOutput(self, node):
        return self.create(node, node.outputs)

    def create(self, node, sockets):
        raise NotImplementedError()

    def getSocketIdentifiers(self):
        raise NotImplementedError()

    def getRelatedPropertyNames(self):
        raise NotImplementedError()

    def apply(self, node, socket):
        raise NotImplementedError()
