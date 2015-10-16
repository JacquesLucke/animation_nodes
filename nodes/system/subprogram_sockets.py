from ... import tree_info

def _updateSubprogramInvokerNodes():
    tree_info.updateIfNecessary()
    for node in tree_info.getNodesByType("an_InvokeSubprogramNode"):
        node.updateSockets()
    tree_info.updateIfNecessary()


subprogramChanged = False

def forceSubprogramUpdate():
    _updateSubprogramInvokerNodes()

def updateIfNecessary():
    global subprogramChanged
    if subprogramChanged: _updateSubprogramInvokerNodes()
    subprogramChanged = False

def subprogramInterfaceChanged():
    from ... events import treeChanged
    global subprogramChanged
    subprogramChanged = True
    treeChanged()


class SubprogramData:
    def __init__(self):
        self.inputs = []
        self.outputs = []

    def newInput(self, idName, identifier, text, defaultValue):
        data = SocketData(idName, identifier, text, defaultValue)
        self.inputs.append(data)

    def newOutput(self, idName, identifier, text, defaultValue = None):
        data = SocketData(idName, identifier, text, defaultValue)
        self.outputs.append(data)

    def newInputFromSocket(self, socket):
        socketData = SocketData.fromSocket(socket)
        self.inputs.append(socketData)
        return socketData

    def newOutputFromSocket(self, socket):
        socketData = SocketData.fromSocket(socket)
        self.outputs.append(socketData)
        return socketData

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
        if newSocket.isInput and not data.defaultValue == NoDefaultValue:
            newSocket.setProperty(data.defaultValue)
        newSocket.text = data.text
        newSocket.display.text = True
        newSocket.dataIsModified = True
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
                          socket.getProperty())


class NoDefaultValue:
    pass
