import bpy
from ... base_types.node import AnimationNode
from ... sockets.info import toIdName

class PrototypeNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_PrototypeNode"
    bl_label = "Prototype Node"
    options = {"No Execution"}

    def draw(self, layout):
        if len(self.sockets) == 0:
            col = layout.column(align = True)
            col.label("Create sockets in the")
            col.label("advanced settings")

    def drawAdvanced(self, layout):
        row = layout.row(align = True)
        self.invokeSocketTypeChooser(row, "newInput", text = "New Input")
        self.invokeSocketTypeChooser(row, "newOutput", text = "New Output")

    def newInput(self, dataType):
        socket = self.inputs.new(toIdName(dataType), dataType)
        self.setupSocket(socket)

    def newOutput(self, dataType):
        socket = self.outputs.new(toIdName(dataType), dataType)
        self.setupSocket(socket)

    def setupSocket(self, socket):
        socket.text = socket.dataType
        socket.textProps.editable = True
        socket.display.textInput = True
        socket.moveable = True
        socket.removeable = True
