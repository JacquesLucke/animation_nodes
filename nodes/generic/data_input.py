import bpy
from bpy.props import *
from ... base_types.node import AnimationNode
from ... sockets.info import toIdName, getSocketClasses

class DataInputNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_DataInputNode"
    bl_label = "Data Input"
    onlySearchTags = True

    @classmethod
    def getSearchTags(cls):
        return [(socket.dataType + " Input", {"assignedType" : repr(socket.dataType)})
                 for socket in getSocketClasses() if socket.hasProperty()]

    def assignedSocketChanged(self, context):
        self.recreateSockets()

    assignedType = StringProperty(default = "Float", update = assignedSocketChanged)
    showInViewport = BoolProperty(default = False, name = "Show in Viewport",
        description = "Draw the input of that node in the 'AN' category of the 3D view (Use the node label as name)")

    def create(self):
        self.recreateSockets()

    def drawAdvanced(self, layout):
        self.invokeSocketTypeChooser(layout, "assignSocketType",
            socketGroup = "ALL", text = "Change Type", icon = "TRIA_RIGHT")

        col = layout.column()
        col.active = self.inputs[0].hasProperty()
        col.prop(self, "showInViewport")

    def getExecutionCode(self):
        # needs no execution, because no value is changed
        return []

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
        drawType = "TEXT_PROPERTY" if socket.dataType == "Boolean" else "PREFER_PROPERTY"
        socket.defaultDrawType = drawType

    def getTemplateCode(self):
        return "self.assignedType = {}".format(repr(self.assignedType))
