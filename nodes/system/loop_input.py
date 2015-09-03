import bpy
from bpy.props import *
from operator import attrgetter
from ... events import networkChanged
from ... utils.names import getRandomString
from ... utils.layout import splitAlignment
from ... tree_info import getNodeByIdentifier
from ... base_types.node import AnimationNode
from . subprogram_sockets import SubprogramData
from ... node_creator import NodeCreator
from . subprogram_base import SubprogramBaseNode
from . utils import updateSubprogramInvokerNodes
from ... sockets.info import (toBaseIdName, toListDataType,
                        toIdName, isBase, toListIdName, toBaseDataType)

class LoopInputNode(bpy.types.Node, AnimationNode, SubprogramBaseNode):
    bl_idname = "an_LoopInputNode"
    bl_label = "Loop Input"

    def create(self):
        self.subprogramName = "Loop"
        self.outputs.new("an_IntegerSocket", "Index")
        self.outputs.new("an_IntegerSocket", "Iterations")
        self.outputs.new("an_NodeControlSocket", "New Iterator").margin = 0.15
        self.outputs.new("an_NodeControlSocket", "New Parameter").margin = 0.15
        self.width = 180

    def draw(self, layout):
        layout.separator()
        layout.prop(self, "subprogramName", text = "", icon = "GROUP_VERTEX")

    def drawAdvanced(self, layout):
        col = layout.column()
        col.label("Description:")
        col.prop(self, "subprogramDescription", text = "")

        layout.separator()

        col = layout.column()
        col.label("Iterator Sockets:")
        box = col.box()
        for socket in self.getIteratorSockets():
            box.prop(socket.loop, "useAsOutput", text = "Use {} as Output".format(repr(socket.text)))
        self.invokeSocketTypeChooser(box, "newIterator", socketGroup = "LIST", text = "New Iterator", icon = "PLUS")

        layout.separator()

        col = layout.column()
        col.label("Parameter Sockets:")
        box = col.box()
        for socket in self.getParameterSockets():
            subcol = box.column(align = False)
            row = subcol.row()
            row.label(repr(socket.text))
            self.invokeFunction(row, "createReassignParameterNode", text = "Reassign", data = socket.identifier)
            row = subcol.row()
            row.prop(socket.loop, "useAsInput", text = "Input")
            row.prop(socket.loop, "useAsOutput", text = "Output")
            subrow = row.row()
            subrow.active = socket.isCopyable
            subrow.prop(socket.loop, "copyAlways", text = "Copy")
            socket.drawSocket(subcol, text = "Default", drawType = "PROPERTY_ONLY")
        self.invokeSocketTypeChooser(box, "newParameter", text = "New Parameter", icon = "PLUS")

        layout.separator()

        col = layout.column()
        col.label("List Generators:")
        box = col.box()
        for node in self.getGeneratorNodes():
            box.label("{} - {}".format(repr(node.outputName), node.listDataType))
        self.invokeSocketTypeChooser(box, "createGeneratorOutputNode", socketGroup = "LIST", text = "New Generator", icon = "PLUS")

    def edit(self):
        for target in self.newIteratorSocket.dataTargets:
            if target.dataType == "Node Control": continue
            if not isBase(target.dataType): continue
            listDataType = toListDataType(target.dataType)
            socket = self.newIterator(listDataType, target.getDisplayedName())
            socket.linkWith(target)

        for target in self.newParameterSocket.dataTargets:
            if target.dataType == "Node Control": continue
            socket = self.newParameter(target.dataType, target.getDisplayedName(), target.getProperty())
            socket.linkWith(target)

        self.newIteratorSocket.removeLinks()
        self.newParameterSocket.removeLinks()

    def drawControlSocket(self, layout, socket):
        isParameterSocket = socket == self.outputs[-1]
        function, socketGroup = ("newParameter", "ALL") if isParameterSocket else ("newIterator", "LIST")

        left, right = splitAlignment(layout)
        self.invokeSocketTypeChooser(left, function, socketGroup = socketGroup, icon = "ZOOMIN", emboss = False)
        right.label(socket.name)


    def newIterator(self, listDataType, name = None):
        if name is None: name = toBaseDataType(listDataType)
        socket = self.outputs.new(toBaseIdName(listDataType), name, "iterator_" + getRandomString(5))
        socket.moveTo(self.newIteratorSocket.index)
        self.setupSocket(socket, name, moveGroup = 1)
        return socket

    def newParameter(self, dataType, name = None, defaultValue = None):
        if name is None: name = dataType
        socket = self.outputs.new(toIdName(dataType), name, "parameter_" + getRandomString(5))
        if defaultValue: socket.setProperty(defaultValue)
        socket.moveTo(self.newParameterSocket.index)
        socket.loop.copyAlways = True
        self.setupSocket(socket, name, moveGroup = 2)
        return socket

    def setupSocket(self, socket, name, moveGroup):
        socket.text = name
        socket.moveGroup = moveGroup
        socket.moveable = True
        socket.removeable = True
        socket.display.text = True
        socket.textProps.editable = True
        socket.display.textInput = True
        socket.display.removeOperator = True
        socket.loop.useAsInput = True


    def socketChanged(self):
        updateSubprogramInvokerNodes()

    def delete(self):
        self.outputs.clear()
        updateSubprogramInvokerNodes()


    def getSocketData(self):
        data = SubprogramData()
        if len(self.outputs) == 0: return data

        self.insertIteratorData(data)
        self.insertGeneratorData(data)
        self.insertParameterData(data)

        return data

    def insertIteratorData(self, data):
        iteratorSockets = self.getIteratorSockets()
        if len(iteratorSockets) == 0:
            data.newInput("an_IntegerSocket", "loop_iterations", "Iterations", 0)
        else:
            for socket in iteratorSockets:
                name = socket.text + " List"
                data.newInput(toListIdName(socket.bl_idname), socket.identifier, name, [])
                if socket.loop.useAsOutput:
                    data.newOutput(toListIdName(socket.bl_idname), socket.identifier, name)

    def insertParameterData(self, data):
        for socket in self.getParameterSockets():
            if socket.loop.useAsInput: data.newInputFromSocket(socket)
            if socket.loop.useAsOutput: data.newOutputFromSocket(socket)

    def insertGeneratorData(self, data):
        for node in self.getGeneratorNodes():
            if node.removed: continue
            data.newOutput(toIdName(node.listDataType), node.identifier, node.outputName)


    def createGeneratorOutputNode(self, dataType):
        GeneratorOutputTemplate(self, dataType)
        updateSubprogramInvokerNodes()

    def createReassignParameterNode(self, socketIdentifier):
        ReassignParameterTemplate(self.outputsByIdentifier[socketIdentifier])
        updateSubprogramInvokerNodes()


    @property
    def newIteratorSocket(self):
        return self.outputs["New Iterator"]

    @property
    def newParameterSocket(self):
        return self.outputs["New Parameter"]

    @property
    def indexSocket(self):
        return self.outputs["Index"]

    @property
    def iterationsSocket(self):
        return self.outputs["Iterations"]

    @property
    def iterateThroughLists(self):
        return len(self.getIteratorSockets()) > 0

    def getIteratorSockets(self):
        return self.outputs[2:self.newIteratorSocket.index]

    def getParameterSockets(self):
        return self.outputs[self.newIteratorSocket.index + 1:self.newParameterSocket.index]

    def getGeneratorNodes(self):
        nodes = self.network.generatorOutputNodes
        nodes.sort(key = attrgetter("sortIndex"))
        return nodes

    def getReassignParameterNodes(self):
        return [node for node in self.network.updateParameterNodes if node.linkedParameterSocket]



class GeneratorOutputTemplate(NodeCreator):
    def insert(self, loopInputNode, dataType):
        node = self.newNode("an_LoopGeneratorOutputNode")
        node.loopInputIdentifier = loopInputNode.identifier
        node.listDataType = dataType

class ReassignParameterTemplate(NodeCreator):
    def insert(self, loopParameterSocket):
        node = self.newNode("an_ReassignLoopParameterNode")
        node.loopInputIdentifier = loopParameterSocket.node.identifier
        node.parameterIdentifier = loopParameterSocket.identifier
