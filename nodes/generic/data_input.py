import bpy
from bpy.props import *
from ... base_types.node import AnimationNode
from ... sockets.mn_socket_info import getSocketDataTypeItems, getIdNameFromDataType


class DataInput(bpy.types.Node, AnimationNode):
    bl_idname = "mn_DataInput"
    bl_label = "Data Input"

    inputNames = { "Input" : "input" }
    outputNames = { "Output" : "output" }

    def assignedSocketChanged(self, context):
        self.recreateSockets()

    selectedType = EnumProperty(name = "Type", items = getSocketDataTypeItems)
    assignedType = StringProperty(default = "Float", update = assignedSocketChanged)

    def create(self):
        self.recreateSockets()

    def draw_buttons_ext(self, context, layout):
        col = layout.column(align = True)
        col.prop(self, "selectedType", text = "")
        self.callFunctionFromUI(col, "assignSelectedType", text = "Assign", description = "Remove all sockets and set the selected socket type")

    def getInLineExecutionString(self, outputUse):
        return "$output$ = %input%"

    def assignSelectedType(self):
        self.assignSocketType(self.selectedType)

    def assignSocketType(self, dataType):
        # this automatically recreates the sockets
        self.assignedType = dataType

    def recreateSockets(self):
        self.inputs.clear()
        self.outputs.clear()

        idName = getIdNameFromDataType(self.assignedType)
        socket = self.inputs.new(idName, "Input")
        self.setupSocket(socket)
        socket = self.outputs.new(idName, "Output")
        self.setupSocket(socket)

    def setupSocket(self, socket):
        socket.displayCustomName = True
        socket.uniqueCustomName = False
        socket.customName = self.assignedType
        if hasattr(socket, "showName"): socket.showName = False
