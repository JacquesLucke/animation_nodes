import bpy
from bpy.props import *
from ... base_types.node import AnimationNode
from ... sockets.info import getDataTypeItems, toIdName


class DataInput(bpy.types.Node, AnimationNode):
    bl_idname = "an_DataInput"
    bl_label = "Data Input"

    def assignedSocketChanged(self, context):
        self.recreateSockets()

    selectedType = EnumProperty(name = "Type", items = getDataTypeItems)
    assignedType = StringProperty(default = "Float", update = assignedSocketChanged)

    def create(self):
        self.recreateSockets()

    def drawAdvanced(self, layout):
        col = layout.column(align = True)
        col.prop(self, "selectedType", text = "")
        self.functionOperator(col, "assignSelectedType", text = "Assign", description = "Remove all sockets and set the selected socket type")

    def getExecutionCode(self):
        return "output = input"

    def assignSelectedType(self):
        self.assignSocketType(self.selectedType)

    def assignSocketType(self, dataType):
        # this automatically recreates the sockets
        self.assignedType = dataType

    def recreateSockets(self):
        self.inputs.clear()
        self.outputs.clear()

        idName = toIdName(self.assignedType)
        socket = self.inputs.new(idName, "Input", "input")
        self.setupSocket(socket)
        socket = self.outputs.new(idName, "Output", "output")
        self.setupSocket(socket)

    def setupSocket(self, socket):
        socket.displayCustomName = True
        socket.nameSettings.unique = False
        socket.customName = self.assignedType
        if hasattr(socket, "showName"): socket.showName = False
