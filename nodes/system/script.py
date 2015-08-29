import bpy
from bpy.props import *
from ... sockets.info import toIdName
from ... events import executionCodeChanged
from ... base_types.node import AnimationNode

class ScriptNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_ScriptNode"
    bl_label = "Script"
    options = {"No Execution"}

    subprogramName = StringProperty()
    subprogramDescription = StringProperty()

    executionCode = StringProperty(default = "")
    textBlockName = StringProperty(default = "")

    def create(self):
        self.width = 200
        self.inputs.new("an_NodeControlSocket", "New Input", "newInput")
        self.outputs.new("an_NodeControlSocket", "New Output", "newOutput")

    def draw(self, layout):
        col = layout.column(align = True)
        col.prop_search(self, "textBlockName",  bpy.data, "texts", text = "")
        row = col.row(align = True)
        self.invokeFunction(row, "writeToTextBlock", text = "Write")
        self.invokeFunction(row, "readFromTextBlock", text = "Read")

        text = self.textInTextBlock
        if text is not None:
            if self.executionCode != text:
                layout.label("Update necessary", icon = "ERROR")

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

    def writeToTextBlock(self):
        if not self.textBlock: return
        self.textBlock.from_string(self.executionCode)

    def readFromTextBlock(self):
        if not self.textBlock: return
        self.executionCode = self.textInTextBlock
        executionCodeChanged()

    @property
    def textInTextBlock(self):
        if self.textBlock:
            return self.textBlock.as_string()
        return None

    @property
    def textBlock(self):
        return bpy.data.texts.get(self.textBlockName)
