import bpy
from bpy.props import *
from operator import attrgetter
from ... events import networkChanged
from ... base_types.node import AnimationNode
from . subprogram_sockets import SubprogramData
from . utils import updateSubprogramInvokerNodes
from ... sockets.info import (toBaseIdName, toListDataType,
                        toIdName, isBase, toListIdName, toBaseDataType)

class LoopInput(bpy.types.Node, AnimationNode):
    bl_idname = "an_LoopInput"
    bl_label = "Loop Input"

    subprogramName = StringProperty(name = "Subprogram Name", default = "Loop",
        description = "Subprogram name to identify this group elsewhere",
        update = networkChanged)

    subprogramDescription = StringProperty(name = "Description", default = "",
        description = "Short description about what this group does",
        update = networkChanged)

    def create(self):
        self.outputs.new("an_IntegerSocket", "Index")
        self.outputs.new("an_IntegerSocket", "Iterations")
        socket = self.outputs.new("an_NodeControlSocket", "New Iterator")
        socket.drawCallback = "drawNewIteratorSocket"
        socket.margin = 0.15
        socket = self.outputs.new("an_NodeControlSocket", "New Parameter")
        socket.drawCallback = "drawNewParameterSocket"
        socket.margin = 0.15
        self.width = 180

    def draw(self, layout):
        layout.separator()
        layout.prop(self, "subprogramName", text = "", icon = "GROUP_VERTEX")
        self.invokeFunction(layout, "createGeneratorOutputNode", text = "New Generator")

    def drawAdvanced(self, layout):
        col = layout.column()
        col.label("Description:")
        col.prop(self, "subprogramDescription", text = "")

        col = layout.column()
        col.label("Parameter Defaults:")
        box = col.box()
        for socket in self.getParameterSockets():
            socket.drawInput(box, self, socket.getDisplayedName())

        col = layout.column()
        col.label("Copy for each Iteration:")
        for socket in self.getParameterSockets():
            row = col.row()
            row.active = socket.isCopyable
            row.prop(socket, "copyAlways", text = socket.text)

    def edit(self):
        for target in self.newIteratorSocket.dataTargets:
            if target.dataType == "Node Control": continue
            if not isBase(target.dataType): continue
            listDataType = toListDataType(target.dataType)
            socket = self.newIterator(listDataType, target.getDisplayedName())
            socket.linkWith(target)

        for target in self.newParameterSocket.dataTargets:
            if target.dataType == "Node Control": continue
            socket = self.newParameter(target.dataType, target.getDisplayedName(), target.getStoreableValue())
            socket.linkWith(target)

        self.newIteratorSocket.removeConnectedLinks()
        self.newParameterSocket.removeConnectedLinks()


    def drawNewIteratorSocket(self, layout):
        row = layout.row()
        subrow = row.row()
        subrow.alignment = "LEFT"
        self.invokeFunction(subrow, "chooseNewIteratorType", icon = "ZOOMIN", emboss = False)
        subrow = row.row()
        subrow.alignment = "RIGHT"
        subrow.label("New Iterator")

    def drawNewParameterSocket(self, layout):
        row = layout.row()
        subrow = row.row()
        subrow.alignment = "LEFT"
        self.invokeFunction(subrow, "chooseNewParameterType", icon = "ZOOMIN", emboss = False)
        subrow = row.row()
        subrow.alignment = "RIGHT"
        subrow.label("New Parameter")


    def chooseNewIteratorType(self):
        self.chooseSocketDataType("newIterator", socketGroup = "LIST")

    def chooseNewParameterType(self):
        self.chooseSocketDataType("newParameter", socketGroup = "ALL")


    def newIterator(self, listDataType, name = None):
        if name is None: name = toBaseDataType(listDataType)
        socket = self.outputs.new(toBaseIdName(listDataType), name, "iterator")
        socket.moveTo(self.newIteratorSocket.index)
        self.setupSocket(socket, name, moveGroup = 1)
        return socket

    def newParameter(self, dataType, name = None, defaultValue = None):
        if name is None: name = dataType
        socket = self.outputs.new(toIdName(dataType), name, "parameter")
        if defaultValue: socket.setStoreableValue(defaultValue)
        socket.moveTo(self.newParameterSocket.index)
        socket.copyAlways = True
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


    def socketChanged(self):
        updateSubprogramInvokerNodes()

    def delete(self):
        self.outputs.clear()
        updateSubprogramInvokerNodes()


    def getSocketData(self):
        data = SubprogramData()
        if len(self.outputs) == 0: return data

        self.insertIteratorData(data)
        self.insertParameterData(data)
        self.insertGeneratorData(data)

        return data

    def insertIteratorData(self, data):
        iteratorSockets = self.getIteratorSockets()
        if len(iteratorSockets) == 0:
            data.newInput("an_IntegerSocket", "loop_iterations", "Iterations", 0)
        else:
            for socket in iteratorSockets:
                data.newInput(toListIdName(socket.bl_idname), socket.identifier, socket.text + " List", [])

    def insertParameterData(self, data):
        for socket in self.getParameterSockets():
            data.newInputFromSocket(socket)

    def insertGeneratorData(self, data):
        for node in self.getGeneratorNodes():
            if node.removed: continue
            data.newOutput(toIdName(node.listDataType), node.identifier, node.outputName, None)


    def createGeneratorOutputNode(self):
        settings = [{"name" : "loopInputIdentifier", "value" : repr(self.identifier)}]
        bpy.ops.node.add_and_link_node("INVOKE_DEFAULT", use_transform = True, settings = settings, type = "an_LoopGeneratorOutput")
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
