import bpy
from bpy.props import *
from ... sockets.info import toIdName
from ... events import executionCodeChanged
from ... base_types.node import AnimationNode
from . subprogram_sockets import SubprogramData
from . utils import updateSubprogramInvokerNodes

class ScriptNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_ScriptNode"
    bl_label = "Script"

    def debugModeChanged(self, context):
        self.errorMessage = ""
        executionCodeChanged()

    subprogramName = StringProperty(default = "Script")
    subprogramDescription = StringProperty()

    executionCode = StringProperty(default = "", update = executionCodeChanged)
    textBlockName = StringProperty(default = "")

    debugMode = BoolProperty(name = "Debug Mode", default = True, update = debugModeChanged)
    errorMessage = StringProperty()

    def create(self):
        self.width = 200
        self.inputs.new("an_NodeControlSocket", "New Input", "newInput")
        self.outputs.new("an_NodeControlSocket", "New Output", "newOutput")

    def draw(self, layout):
        col = layout.column(align = True)
        row = col.row(align = True)
        self.invokeFunction(row, "createNewTextBlock", icon = "ZOOMIN")
        row.prop_search(self, "textBlockName",  bpy.data, "texts", text = "")
        subrow = row.row(align = True)
        subrow.active = self.textBlock is not None
        self.invokeFunction(subrow, "writeToTextBlock", icon = "COPYDOWN",
            description = "Write script code into the selected text block.")

        subcol = col.column(align = True)
        subcol.scale_y = 1.4
        subcol.active = self.textBlock is not None

        icon = "NONE"
        text = self.textInTextBlock
        if text is not None:
            if self.executionCode != text: icon = "ERROR"

        self.invokeFunction(subcol, "readFromTextBlock", text = "Read", icon = icon)

        layout.prop(self, "subprogramName", text = "")

        if self.errorMessage != "":
            layout.label(self.errorMessage, icon = "ERROR")

    def drawAdvanced(self, layout):
        col = layout.column()
        col.label("Description:")
        col.prop(self, "subprogramDescription", text = "")
        layout.prop(self, "debugMode")

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
        socket.display.removeOperator = True
        socket.moveable = True
        socket.removeable = True
        socket.moveUp()
        socket.text = socket.dataType

    def socketChanged(self):
        updateSubprogramInvokerNodes()

    def delete(self):
        self.inputs.clear()
        self.outputs.clear()
        updateSubprogramInvokerNodes()

    def getSocketData(self):
        data = SubprogramData()
        for socket in self.inputs[:-1]:
            data.newInputFromSocket(socket)
        for socket in self.outputs[:-1]:
            data.newOutputFromSocket(socket)
        return data

    def createNewTextBlock(self):
        textBlock = bpy.data.texts.new(name = self.subprogramName)
        self.textBlockName = textBlock.name
        self.writeToTextBlock()

    def writeToTextBlock(self):
        if not self.textBlock: return
        self.textBlock.from_string(self.executionCode)

    def readFromTextBlock(self):
        if not self.textBlock: return
        self.executionCode = self.textInTextBlock
        self.errorMessage = ""

    @property
    def textInTextBlock(self):
        if self.textBlock:
            return self.textBlock.as_string()
        return None

    @property
    def textBlock(self):
        return bpy.data.texts.get(self.textBlockName)
