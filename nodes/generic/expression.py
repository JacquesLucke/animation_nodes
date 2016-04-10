import re
import bpy
from bpy.props import *
from ... sockets.info import toIdName
from ... utils.code import isCodeValid
from ... utils.layout import splitAlignment
from ... events import executionCodeChanged
from ... base_types.node import AnimationNode

variableNames = list("xyzabcdefghijklmnopqrstuvw")

class ExpressionNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_ExpressionNode"
    bl_label = "Expression"
    bl_width_default = 200

    def settingChanged(self, context = None):
        self.executionError = ""
        self.containsSyntaxError = not isCodeValid(self.expression)
        executionCodeChanged()

    def outputTypeChanged(self, context):
        self.recreateOutputSocket()

    expression = StringProperty(name = "Expression", update = settingChanged)
    containsSyntaxError = BoolProperty()
    executionError = StringProperty()

    debugMode = BoolProperty(name = "Debug Mode", update = executionCodeChanged, default = True,
        description = "Show detailed error messages in the node but is slower.")

    moduleNames = StringProperty(name = "Modules", default = "math", update = executionCodeChanged,
        description = "Comma separated module names which can be used inside the expression")

    outputIsList = BoolProperty(name = "Output is List", default = False, update = outputTypeChanged)

    def create(self):
        self.newInput("an_NodeControlSocket", "New Input")
        self.newOutput("an_GenericSocket", "Result", "result")

    def recreateOutputSocket(self):
        idName = "an_GenericListSocket" if self.outputIsList else "an_GenericSocket"
        if self.outputs[0].bl_idname == idName: return
        self.outputs.clear()
        self.newOutput(idName, "Result", "result")

    def draw(self, layout):
        layout.prop(self, "expression", text = "")
        if self.containsSyntaxError:
            layout.label("Syntax Error", icon = "ERROR")
        if self.executionError != "":
            row = layout.row()
            row.label(self.executionError, icon = "ERROR")
            self.invokeFunction(row, "clearErrorMessage", icon = "X", emboss = False)

    def drawAdvanced(self, layout):
        layout.prop(self, "debugMode")
        layout.prop(self, "outputIsList")
        layout.prop(self, "moduleNames")

    def drawControlSocket(self, layout, socket):
        left, right = splitAlignment(layout)
        left.label(socket.name)
        self.invokeSocketTypeChooser(right, "newInputSocket", icon = "ZOOMIN", emboss = False)

    @property
    def inputVariables(self):
        return {socket.identifier : socket.text for socket in self.inputs}

    def getExecutionCode(self):
        expression = self.expression.strip()

        if self.debugMode:
            if expression == "" or self.containsSyntaxError:
                return "result = None"
            return ["try:",
                    "    result = " + expression,
                    "    self.executionError = ''",
                    "except:",
                    "    result = None",
                    "    self.executionError = str(sys.exc_info()[1])"]
        else: return "result = " + expression

    def getUsedModules(self):
        moduleNames = re.split("\W+", self.moduleNames)
        modules = [module for module in moduleNames if module != ""]
        return ["sys"] + modules

    def clearErrorMessage(self):
        self.executionError = ""

    def edit(self):
        emptySocket = self.inputs["New Input"]
        directOrigin = emptySocket.directOrigin
        if directOrigin is None: return
        dataOrigin = emptySocket.dataOrigin
        if dataOrigin.dataType == "Node Control": return
        socket = self.newInputSocket(dataOrigin.dataType)
        emptySocket.removeLinks()
        socket.linkWith(directOrigin)

    def newInputSocket(self, dataType):
        name = self.getNewSocketName()
        socket = self.newInput(toIdName(dataType), name, "input")
        socket.dataIsModified = True
        socket.textProps.editable = True
        socket.textProps.variable = True
        socket.textProps.unique = True
        socket.display.text = True
        socket.display.textInput = True
        socket.text = name
        socket.moveable = True
        socket.removeable = True
        socket.moveUp()
        if len(self.inputs) > 2:
            socket.copyDisplaySettingsFrom(self.inputs[0])
        return socket

    def getNewSocketName(self):
        inputs = self.inputsByText
        for name in variableNames:
            if name not in inputs: return name
        return "x"

    def socketChanged(self):
        self.settingChanged()
        executionCodeChanged()
