class DynamicSocketSet:
    def __init__(self):
        self.loadDefaults()
        self.loadStates()

    def loadDefaults(self):
        self.inputs = []
        self.outputs = []
        self.defaults()

    def defaults(self):
        raise NotImplementedError()

    def createDefaults(self, node):
        node.clearSockets()
        for socket in self.inputs:
            dataType = socket.defaultDataType
            name, identifier, kwargs = socket.getState(dataType)
            node.newInput(dataType, name, identifier, **kwargs)
        for socket in self.outputs:
            dataType = socket.defaultDataType
            name, identifier, kwargs = socket.getState(dataType)
            node.newOutput(dataType, name, identifier, **kwargs)

    def newInput(self, dataType, name, identifier, **kwargs):
        socket = SocketInfo(dataType)
        socket.addState(dataType, name, identifier, kwargs)
        self.inputs.append(socket)

    def newOutput(self, dataType, name, identifier, **kwargs):
        socket = SocketInfo(dataType)
        socket.addState(dataType, name, identifier, kwargs)
        self.outputs.append(socket)

    def loadStates(self):
        self.states(self.inputs, self.outputs)

    def states(self, inputs, outputs):
        raise NotImplementedError()

    def setState(self, socket, dataType, name, identifier, **kwargs):
        socket.addState(dataType, name, identifier, kwargs)

    def applyRules(self, node):
        self.newTypes = dict()
        for socket, socketInfo in zip(node.inputs, self.inputs):
            self.newTypes[socket] = socketInfo.defaultDataType
        for socket, socketInfo in zip(node.outputs, self.outputs):
            self.newTypes[socket] = socketInfo.defaultDataType

        self.rules(list(node.inputs), list(node.outputs))

        for i, socket in enumerate(node.inputs):
            dataType = self.newTypes[socket]
            if socket.dataType != dataType:
                self.inputs[i].assign(node, socket, dataType)

        for i, socket in enumerate(node.outputs):
            dataType = self.newTypes[socket]
            if socket.dataType != dataType:
                self.outputs[i].assign(node, socket, dataType)

    def rules(self, inputs, outputs):
        raise NotImplementedError()

    def setType(self, socket, dataType):
        self.newTypes[socket] = dataType

class SocketInfo:
    def __init__(self, defaultDataType):
        self.defaultDataType = defaultDataType
        self.states = dict()

    def addState(self, dataType, name, identifier, kwargs):
        self.states[dataType] = (name, identifier, kwargs)

    def getState(self, dataType):
        return self.states[dataType]

    def assign(self, node, socket, dataType):
        name, identifier, kwargs = self.states[dataType]
        node.replaceSocket(socket, dataType, name, identifier, **kwargs)
