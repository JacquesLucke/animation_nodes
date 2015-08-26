class SubprogramData:
    def __init__(self):
        self.inputs = []
        self.outputs = []

    def newInput(self, idName, identifier, text, defaultValue):
        data = SocketData(idName, identifier, text, defaultValue)
        self.inputs.append(data)

    def newOutput(self, idName, identifier, text, defaultValue):
        data = SocketData(idName, identifier, text, defaultValue)
        self.outputs.append(data)

    def newInputFromSocket(self, socket):
        self.inputs.append(SocketData.fromSocket(socket))

    def newOutputFromSocket(self, socket):
        self.outputs.append(SocketData.fromSocket(socket))

    def apply(self, node):
        self.applyInputs(node)
        self.applyOutputs(node)

    def applyInputs(self, node):
        self.applySockets(node, node.inputsByIdentifier, node.inputs, self.inputs)

    def applyOutputs(self, node):
        self.applySockets(node, node.outputsByIdentifier, node.outputs, self.outputs)

    def applySockets(self, node, oldSockets, nodeSockets, socketData):
        for i, data in enumerate(socketData):
            couldUseOldSocket = self.changeExistingSocket(oldSockets, data, i)
            if couldUseOldSocket: continue
            newSocket = self.newSocketFromData(nodeSockets, data)
            newSocket.moveTo(i)

        self.removeUnusedSockets(nodeSockets, socketData)

    def changeExistingSocket(self, oldSockets, data, targetIndex):
        if data.identifier in oldSockets:
            socket = oldSockets[data.identifier]
            if socket.bl_idname == data.idName:
                socket.moveTo(targetIndex)
                socket.text = data.text
                return True
            else:
                socket.remove()
        return False

    def newSocketFromData(self, nodeSockets, data):
        newSocket = nodeSockets.new(data.idName, data.identifier, data.identifier)
        if newSocket.isInput: newSocket.setStoreableValue(data.defaultValue)
        newSocket.text = data.text
        newSocket.display.text = True
        return newSocket

    def removeUnusedSockets(self, nodeSockets, socketData):
        for socket in nodeSockets[len(socketData):]:
            socket.remove()

class SocketData:
    def __init__(self, idName, identifier, text, defaultValue):
        self.idName = idName
        self.identifier = identifier
        self.text = text
        self.defaultValue = defaultValue

    @staticmethod
    def fromSocket(socket):
        return SocketData(socket.bl_idname,
                          socket.identifier,
                          socket.text,
                          socket.getStoreableValue())
