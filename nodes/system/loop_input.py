import bpy
from bpy.props import *
from . utils import updateCallerNodes
from ... events import networkChanged
from ... base_types.node import AnimationNode
from . subprogram_sockets import SubprogramData
from ... sockets.info import toBaseIdName, toListDataType, toIdName, isBase

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
        socket = self.outputs.new("an_NodeControlSocket", "New Iterator")
        socket.drawCallback = "drawNewIteratorSocket"
        socket = self.outputs.new("an_NodeControlSocket", "New Parameter")
        socket.drawCallback = "drawNewParameterSocket"
        self.width = 180

    def draw(self, layout):
        layout.separator()
        layout.prop(self, "subprogramName", text = "", icon = "GROUP_VERTEX")

    def drawAdvanced(self, layout):
        col = layout.column()
        col.label("Description:")
        col.prop(self, "subprogramDescription", text = "")

        col = layout.column()
        col.label("Parameter Defaults:")
        box = col.box()
        for socket in self.getParameterSockets():
            socket.drawInput(box, self, socket.getDisplayedName())

    def edit(self):
        for target in self.newIteratorSocket.dataTargetSockets:
            if target.dataType == "Node Control": continue
            if not isBase(target.dataType): continue
            listDataType = toListDataType(target.dataType)
            socket = self.newIterator(listDataType, target.getDisplayedName())
            socket.linkWith(target)

        for target in self.newParameterSocket.dataTargetSockets:
            if target.dataType == "Node Control": continue
            socket = self.newParameter(target.dataType, target.getDisplayedName(), target.getStoreableValue())
            socket.linkWith(target)

        self.newIteratorSocket.removeConnectedLinks()
        self.newParameterSocket.removeConnectedLinks()


    def drawNewIteratorSocket(self, layout):
        self.drawOperatorInMargin(layout, "chooseNewIteratorType", "New Iterator")

    def drawNewParameterSocket(self, layout):
        self.drawOperatorInMargin(layout, "chooseNewParameterType", "New Parameter")

    def drawOperatorInMargin(self, layout, functionName, text):
        col = layout.column()
        col.alignment = "RIGHT"
        col.separator()
        self.functionOperator(col, functionName, text = text, emboss = False)
        col.separator()
        col.scale_y = 0.8

    def chooseNewIteratorType(self):
        self.chooseSocketDataType("newIterator", socketGroup = "LIST")

    def chooseNewParameterType(self):
        self.chooseSocketDataType("newParameter", socketGroup = "ALL")


    def newIterator(self, listDataType, name = "Socket"):
        socket = self.outputs.new(toBaseIdName(listDataType), name, "iterator")
        socket.moveTo(self.newIteratorSocket.index)
        self.setupSocket(socket, name, moveGroup = 1)
        return socket

    def newParameter(self, dataType, name = "Socket", defaultValue = None):
        socket = self.outputs.new(toIdName(dataType), name, "parameter")
        socket.moveTo(self.newParameterSocket.index)
        self.setupSocket(socket, name, moveGroup = 2)
        return socket

    def setupSocket(self, socket, name, moveGroup):
        socket.customName = name
        socket.moveGroup = moveGroup
        socket.moveable = True
        socket.removeable = True
        socket.displayCustomName = True
        socket.nameSettings.editable = True
        socket.display.customNameInput = True
        socket.display.removeOperator = True


    @property
    def newIteratorSocket(self):
        return self.outputs["New Iterator"]

    @property
    def newParameterSocket(self):
        return self.outputs["New Parameter"]

    def getParameterSockets(self):
        return self.outputs[self.newIteratorSocket.index + 1:self.newParameterSocket.index]
