import bpy
from collections import OrderedDict, defaultdict
from ... utils.attributes import setattrRecursive, getattrRecursive
from ... sockets.info import (isBase, isList, toBaseDataType, toListDataType,
                              getAllowedInputDataTypes, getAllowedTargetDataTypes)

class SocketEffect:
    def apply(self, node):
        pass

    def toSocketIDs(self, sockets, node = None):
        return [self.toSocketID(socket, node) for socket in sockets if socket is not None]

    def toSocketID(self, socket, node = None):
        return socket.isOutput, socket.getIndex(node)

    def getSocket(self, node, socketID):
        return (node.outputs if socketID[0] else node.inputs)[socketID[1]]

class AutoSelectVectorization(SocketEffect):
    def __init__(self):
        self.properties = list()
        self.inputDependencies = OrderedDict()
        self.inputSocketIndicesByProperty = OrderedDict()
        self.inputListDataTypes = dict()
        self.inputBaseDataTypes = dict()
        self.outputDependencies = OrderedDict()
        self.outputListDataTypes = dict()

    def input(self, node, propertyName, sockets, isCurrentlyList, dependencies = []):
        if isinstance(sockets, bpy.types.NodeSocket):
            sockets = [sockets]
        if any(socket.is_output for socket in sockets):
            raise ValueError("only input sockets allowed")

        self.setSocketTransparency(sockets)

        self.properties.append(propertyName)
        socketIndices = [socket.getIndex(node) for socket in sockets]
        self.inputSocketIndicesByProperty[propertyName] = socketIndices
        self.inputDependencies[propertyName] = dependencies

        if isCurrentlyList:
            self.inputListDataTypes[propertyName] = (
                {index : getAllowedInputDataTypes(socket.dataType)
                 for socket, index in zip(sockets, socketIndices)})
            self.inputBaseDataTypes[propertyName] = (
                {index : getAllowedInputDataTypes(toBaseDataType(socket.dataType))
                 for socket, index in zip(sockets, socketIndices)})
        else:
            self.inputListDataTypes[propertyName] = (
                {index : getAllowedInputDataTypes(toListDataType(socket.dataType))
                 for socket, index in zip(sockets, socketIndices)})
            self.inputBaseDataTypes[propertyName] = (
                {index : getAllowedInputDataTypes(socket.dataType)
                 for socket, index in zip(sockets, socketIndices)})

    def output(self, node, dependencies, sockets, isCurrentlyList):
        if isinstance(sockets, bpy.types.NodeSocket):
            sockets = [sockets]
        if any(not socket.is_output for socket in sockets):
            raise ValueError("only output sockets allowed")

        if isinstance(dependencies, str):
            dependencies = [dependencies]

        self.setSocketTransparency(sockets)

        for socket in sockets:
            self.outputDependencies[socket.getIndex(node)] = dependencies
            if isCurrentlyList: listType = socket.dataType
            else: listType = toListDataType(socket.dataType)
            self.outputListDataTypes[socket.dataType] = getAllowedTargetDataTypes(listType)

    def setSocketTransparency(self, sockets):
        for socket in sockets:
            if isBase(socket.dataType):
                socket.setTemporarySocketTransparency(0.80)

    def apply(self, node):
        # Set default state to BASE
        states = {propertyName : "BASE" for propertyName in self.properties}
        fixedProperties = set()

        # Evaluate linked input sockets
        for propertyName, inputIndices in self.inputSocketIndicesByProperty.items():
            for index in inputIndices:
                socket = node.inputs[index]
                linkedDataTypes = tuple(socket.linkedDataTypes - {"Generic"})
                if len(linkedDataTypes) == 1:
                    linkedType = linkedDataTypes[0]
                    if linkedType in self.inputListDataTypes[propertyName][index]:
                        states[propertyName] = "LIST"
                        fixedProperties.add(propertyName)
                    elif linkedType in self.inputBaseDataTypes[propertyName][index]:
                        states[propertyName] = "BASE"
                        fixedProperties.add(propertyName)

        # Evaluate input dependencies
        for propertyName, dependencyNames in self.inputDependencies.items():
            if states[propertyName] == "LIST":
                if any(states[name] == "BASE" and name in fixedProperties for name in dependencyNames):
                    states[propertyName] = "BASE"
                else:
                    for name in dependencyNames:
                        states[name] = "LIST"
                        fixedProperties.add(name)
                fixedProperties.add(propertyName)

        # Evaluate output dependencies
        for socketIndex, dependencies in self.outputDependencies.items():
            socket = node.outputs[socketIndex]
            linkedTypes = tuple(socket.linkedDataTypes - {"Generic"})
            if len(linkedTypes) != 1:
                continue
            linkedType = linkedTypes[0]
            if linkedType in self.outputListDataTypes[socket.dataType]:
                for dependency in dependencies:
                    if isinstance(dependency, str):
                        if dependency not in fixedProperties:
                            states[dependency] = "LIST"
                            fixedProperties.add(dependency)
                    elif isinstance(dependency, (set, list, tuple)):
                        if all(states[name] == "BASE" for name in dependency):
                            for name in dependency:
                                if name not in fixedProperties:
                                    states[name] = "LIST"
                                    fixedProperties.add(name)
                                    break

        # Update properties of node
        for propertyName in self.properties:
            state = states[propertyName] == "LIST"
            if state != getattrRecursive(node, propertyName):
                setattrRecursive(node, propertyName, state)
