class SocketEffect:
    def apply(self, node):
        pass

    def toSocketID(self, socket):
        return socket.isOutput, socket.getIndex()

    def getSocket(self, node, socketID):
        return (node.outputs if socketID[0] else node.inputs)[socketID[1]]


class AutoSelectFloatOrInteger(SocketEffect):
    def __init__(self, socket):
        self.socketID = self.toSocketID(socket)

    def apply(self, node):
        socket = self.getSocket(node, self.socketID)
        if socket.dataType == "Float":
            if socket.shouldBeIntegerSocket():
                node.replaceSocket(socket, "Integer", socket.name, socket.identifier)
        elif socket.dataType == "Integer":
            if socket.shouldBeFloatSocket():
                node.replaceSocket(socket, "Float", socket.name, socket.identifier)


from .. sockets.info import isBase, isList, toBaseDataType, toListDataType
class UpdateAssignedListDataType(SocketEffect):
    def __init__(self, propertyName, propertyType, sockets):
        self.propertyName = propertyName
        self.propertyType = propertyType
        self.socketIDs = []
        self.checkFunctions = []
        for socket, mode in sockets:
            if mode == "IGNORE": continue
            self.socketIDs.append(self.toSocketID(socket))
            if socket.isInput:
                if mode == "BASE":
                    self.checkFunctions.append(self.getLinkedBaseType_BaseInput)
                elif mode == "LIST":
                    self.checkFunctions.append(self.getLinkedBaseType_ListInput)
            else:
                if mode == "BASE":
                    self.checkFunctions.append(self.getLinkedBaseType_BaseOutput)
                else:
                    self.checkFunctions.append(self.getLinkedBaseType_ListOutput)

    def apply(self, node):
        currentType = getattr(node, self.propertyName)
        for socketID, getLinkedBaseType in zip(self.socketIDs, self.checkFunctions):
            linkedType = getLinkedBaseType(self.getSocket(node, socketID))
            if linkedType is not None:
                if self.propertyType == "LIST":
                    linkedType = toListDataType(linkedType)
                if linkedType != currentType:
                    setattr(node, self.propertyName, linkedType)
                break

    def getLinkedBaseType_BaseInput(self, socket):
        dataOrigin = socket.dataOrigin
        if dataOrigin is not None:
            if isBase(dataOrigin.dataType):
                return dataOrigin.dataType

    def getLinkedBaseType_ListInput(self, socket):
        dataOrigin = socket.dataOrigin
        if dataOrigin is not None:
            if isList(dataOrigin.dataType):
                return toBaseDataType(dataOrigin.dataType)

    def getLinkedBaseType_BaseOutput(self, socket):
        linkedDataTypes = tuple(socket.linkedDataTypes)
        if len(linkedDataTypes) == 1:
            if isBase(linkedDataTypes[0]):
                return linkedDataTypes[0]

    def getLinkedBaseType_ListOutput(self, socket):
        linkedDataTypes = tuple(socket.linkedDataTypes)
        if len(linkedDataTypes) == 1:
            if isList(linkedDataTypes[0]):
                return toBaseDataType(linkedDataTypes[0])


class UpdateAssignedDataType(SocketEffect):
    def __init__(self, propertyName, sockets, ignore = set(), default = None):
        self.propertyName = propertyName
        self.ignoredDataTypes = set(ignore)
        self.default = default
        self.socketIDs = [self.toSocketID(socket) for socket in sockets if socket is not None]

    def apply(self, node):
        currentType = getattr(node, self.propertyName)
        for socketID in self.socketIDs:
            socket = self.getSocket(node, socketID)
            linkedDataTypes = tuple(socket.linkedDataTypes - self.ignoredDataTypes)

            if len(linkedDataTypes) == 1:
                if linkedDataTypes[0] != currentType:
                    setattr(node, self.propertyName, linkedDataTypes[0])
                break
            elif len(linkedDataTypes) == 0 and self.default is not None:
                if self.default != currentType:
                    setattr(node, self.propertyName, self.default)
