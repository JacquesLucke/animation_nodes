import bpy
from bpy.props import *
from ... base_types.node import AnimationNode
from ... sockets.info import getDataTypeItems, toIdName, getDataTypes

class DataInputNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_DataInputNode"
    bl_label = "Data Input"

    @classmethod
    def getSearchTags(cls):
        return [(dataType + " Input", {"assignedType" : repr(dataType)}) for dataType in getDataTypes()]

    def assignedSocketChanged(self, context):
        self.recreateSockets()

    selectedType = EnumProperty(name = "Type", items = getDataTypeItems)
    assignedType = StringProperty(default = "Float", update = assignedSocketChanged)
    showInViewport = BoolProperty(default = False, name = "Show in Viewport",
        description = "Draw the input of that node in the 'AN' category of the 3D view (Use the node label as name)")

    def create(self):
        self.recreateSockets()

    def drawAdvanced(self, layout):
        col = layout.column(align = True)
        col.prop(self, "selectedType", text = "")
        self.invokeFunction(col, "assignSelectedType", text = "Assign", description = "Remove all sockets and set the selected socket type")

        col = layout.column()
        col.active = self.inputs[0].hasProperty
        col.prop(self, "showInViewport")

    def getExecutionCode(self):
        # needs no execute
        return []

    def assignSelectedType(self):
        self.assignSocketType(self.selectedType)

    def assignSocketType(self, dataType):
        # this automatically recreates the sockets
        self.assignedType = dataType

    def recreateSockets(self):
        self.inputs.clear()
        self.outputs.clear()

        idName = toIdName(self.assignedType)
        socket = self.inputs.new(idName, "Input", "value")
        socket.dataIsModified = True
        self.setupSocket(socket)
        socket = self.outputs.new(idName, "Output", "value")
        self.setupSocket(socket)

    def setupSocket(self, socket):
        socket.display.text = True
        socket.text = self.assignedType
        socket.defaultDrawType = "PREFER_PROPERTY"
