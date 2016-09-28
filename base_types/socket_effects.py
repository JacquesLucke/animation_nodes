from .. sockets.info import isBase, isList, toBaseDataType, toListDataType

class SocketEffect:
    def apply(self, node):
        pass

    def toSocketIDs(self, sockets):
        return [self.toSocketID(socket) for socket in sockets if socket is not None]

    def toSocketID(self, socket):
        return socket.isOutput, socket.getIndex()

    def getSocket(self, node, socketID):
        return (node.outputs if socketID[0] else node.inputs)[socketID[1]]


class AutoSelectFloatOrInteger(SocketEffect):
    def __init__(self, propertyName, socket):
        self.socketID = self.toSocketID(socket)
        self.propertyName = propertyName

    def apply(self, node):
        socket = self.getSocket(node, self.socketID)
        linkedDataTypes = socket.linkedDataTypes - {"Generic"}
        if socket.dataType == "Float":
            if linkedDataTypes == {"Integer"}:
                setattr(node, self.propertyName, "Integer")
        elif socket.dataType == "Integer":
            if linkedDataTypes == {"Float"}:
                setattr(node, self.propertyName, "Float")


class AutoSelectListDataType(SocketEffect):
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


class AutoSelectDataType(SocketEffect):
    def __init__(self, propertyName, sockets, ignore = set(), default = None):
        self.propertyName = propertyName
        self.ignoredDataTypes = set(ignore)
        self.default = default
        self.socketIDs = self.toSocketIDs(sockets)

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


class AutoSelectVectorization(SocketEffect):
    def __init__(self):
        self.properties = {}

    def add(self, propertyName, sockets, dependency = None):
        if dependency is None:
            dependencies = set()
        elif isinstance(dependency, str):
            dependencies = set([dependency])
        else:
            dependencies = set(dependency)
        self.properties[propertyName] = (self.toSocketIDs(sockets), dependencies)

    def apply(self, node):
        propertyStates = {propertyName : "BASE" for propertyName in self.properties.keys()}
        fixedProperties = set()

        for propertyName, (socketIDs, _) in self.properties.items():
            for socketID in socketIDs:
                socket = self.getSocket(node, socketID)
                linkedDataTypes = tuple(socket.linkedDataTypes - {"Generic"})
                if len(linkedDataTypes) == 1:
                    if isList(linkedDataTypes[0]):
                        propertyStates[propertyName] = "LIST"
                        fixedProperties.add(propertyName)
                    elif isBase(linkedDataTypes[0]):
                        propertyStates[propertyName] = "BASE"
                        fixedProperties.add(propertyName)
                    break

        for propertyName, (_, dependencies) in self.properties.items():
            targetState = propertyStates[propertyName]
            if targetState == "LIST":
                baseDependencies = {dependency for dependency in dependencies if propertyStates[dependency] == "BASE"}
                if len(baseDependencies) > 0:
                    if any(dependency in fixedProperties for dependency in baseDependencies):
                        propertyStates[propertyName] = "BASE"
                    else:
                        for dependency in baseDependencies:
                            propertyStates[dependency] = "LIST"

        for propertyName in self.properties.keys():
            state = propertyStates[propertyName] == "LIST"
            if state != getattr(node, propertyName):
                setattr(node, propertyName, state)
