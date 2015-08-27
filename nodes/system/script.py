import bpy
from ... sockets.info import toIdName
from ... base_types.node import AnimationNode

class ScriptNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_ScriptNode"
    bl_label = "Script"
    options = {"No Execution"}

    def create(self):
        self.width = 200
        self.inputs.new("an_NodeControlSocket", "New Input", "newInput")
        self.outputs.new("an_NodeControlSocket", "New Output", "newOutput")

    def drawControlSocket(self, layout, socket):
        if socket in list(self.inputs):
            self.invokeSocketTypeChooser(layout, "newInput", text = "New Input", icon = "ZOOMIN")
        else:
            self.invokeSocketTypeChooser(layout, "newOutput", text = "New Output", icon = "ZOOMIN")

    def edit(self):
        for socket in self.sockets:
            socket.removeLinks()

    def newInput(self, dataType):
        socket = self.inputs.new(toIdName(dataType), dataType)
        self.setupSocket(socket)

    def newOutput(self, dataType):
        socket = self.outputs.new(toIdName(dataType), dataType)
        self.setupSocket(socket)

    def setupSocket(self, socket):
        socket.textProps.editable = True
        socket.textProps.variable = True
        socket.textProps.unique = True
        socket.display.textInput = True
        socket.display.text = True
        socket.moveable = True
        socket.removeable = True
        socket.moveUp()
        socket.text = socket.dataType
