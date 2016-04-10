import bpy
from bpy.props import *
from ... sockets.info import toIdName
from ... tree_info import getNodesByType
from ... ui.info_popups import showTextPopup
from ... utils.handlers import eventHandler
from ... utils.names import toInterfaceName
from ... events import executionCodeChanged
from ... base_types.node import AnimationNode
from ... utils.blender_ui import getAreaWithType
from . subprogram_base import SubprogramBaseNode
from ... execution.units import getSubprogramUnitByIdentifier
from . subprogram_sockets import SubprogramData, subprogramInterfaceChanged

class ScriptNode(bpy.types.Node, AnimationNode, SubprogramBaseNode):
    bl_idname = "an_ScriptNode"
    bl_label = "Script"
    bl_width_default = 200

    def debugModeChanged(self, context):
        self.errorMessage = ""
        executionCodeChanged()

    executionCode = StringProperty(default = "")
    textBlockName = StringProperty(default = "")

    debugMode = BoolProperty(name = "Debug Mode", default = True,
        description = "Give error message inside the node", update = debugModeChanged)
    errorMessage = StringProperty()

    interactiveMode = BoolProperty(name = "Interactive Mode", default = True,
        description = "Recompile the script on each change in the text block")

    def create(self):
        self.randomizeNetworkColor()
        self.subprogramName = "My Script"
        self.newInput("an_NodeControlSocket", "New Input", "newInput")
        self.newOutput("an_NodeControlSocket", "New Output", "newOutput")

    def draw(self, layout):
        layout.separator()

        col = layout.column(align = True)
        row = col.row(align = True)
        self.invokeFunction(row, "createNewTextBlock", icon = "ZOOMIN")
        row.prop_search(self, "textBlockName",  bpy.data, "texts", text = "")
        subrow = row.row(align = True)
        subrow.active = self.textBlock is not None
        self.invokeFunction(subrow, "writeToTextBlock", icon = "COPYDOWN",
            description = "Write script code into the selected text block")

        subcol = col.column(align = True)
        subcol.scale_y = 1.4
        subcol.active = self.textBlock is not None

        icon = "NONE"
        text = self.textInTextBlock
        if text is not None:
            if self.executionCode != text: icon = "ERROR"

        if not self.interactiveMode:
            self.invokeFunction(subcol, "readFromTextBlock", text = "Import Changes", icon = icon,
                description = "Import the changes from the selected text block")

        layout.prop(self, "subprogramName", text = "", icon = "GROUP_VERTEX")

        if self.errorMessage != "":
            layout.label(self.errorMessage, icon = "ERROR")

        layout.separator()

    def drawAdvanced(self, layout):
        col = layout.column()
        col.label("Description:")
        col.prop(self, "subprogramDescription", text = "")
        layout.prop(self, "debugMode")
        layout.prop(self, "interactiveMode")

    def drawControlSocket(self, layout, socket):
        if socket in list(self.inputs):
            self.invokeSocketTypeChooser(layout, "newInput", text = "New Input", icon = "ZOOMIN")
        else:
            self.invokeSocketTypeChooser(layout, "newOutput", text = "New Output", icon = "ZOOMIN")

    def edit(self):
        removedLink = self.removeLinks()
        if removedLink:
            text = "Please use an 'Invoke Subprogram' node to execute the script node"
            showTextPopup(text = text, title = "Info", icon = "INFO")

    def newInput(self, dataType):
        socket = self.newInput(toIdName(dataType), dataType)
        self.setupSocket(socket)

    def newOutput(self, dataType):
        socket = self.newOutput(toIdName(dataType), dataType)
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
        subprogramInterfaceChanged()

    def delete(self):
        self.inputs.clear()
        self.outputs.clear()
        subprogramInterfaceChanged()

    def duplicate(self, sourceNode):
        self.randomizeNetworkColor()
        self.textBlockName = ""

    def getSocketData(self):
        data = SubprogramData()
        for socket in self.inputs[:-1]:
            socketData = data.newInputFromSocket(socket)
            socketData.text = toInterfaceName(socket.text)
        for socket in self.outputs[:-1]:
            socketData = data.newOutputFromSocket(socket)
            socketData.text = toInterfaceName(socket.text)
        return data

    def createNewTextBlock(self):
        textBlock = bpy.data.texts.new(name = self.subprogramName + " Code")
        self.textBlockName = textBlock.name
        self.writeToTextBlock()
        area = getAreaWithType("TEXT_EDITOR")
        if area: area.spaces.active.text = textBlock

    def writeToTextBlock(self):
        if not self.textBlock: return
        self.textBlock.from_string(self.executionCode)

    def readFromTextBlock(self):
        if not self.textBlock: return
        self.executionCode = self.textInTextBlock
        self.errorMessage = ""
        executionCodeChanged()

    def interactiveUpdate(self):
        if not self.textBlock: return
        text = self.textInTextBlock
        if self.executionCode == text: return
        executionUnit = self.executionUnit
        if executionUnit is None: return
        self.executionCode = text
        executionUnit.scriptUpdated()

    @property
    def textInTextBlock(self):
        if self.textBlock:
            return self.textBlock.as_string()
        return None

    @property
    def textBlock(self):
        return bpy.data.texts.get(self.textBlockName)

    @property
    def executionUnit(self):
        return getSubprogramUnitByIdentifier(self.identifier)


@eventHandler("SCENE_UPDATE_POST")
def sceneUpdate(scene):
    for node in getNodesByType("an_ScriptNode"):
        if node.interactiveMode:
            node.interactiveUpdate()
