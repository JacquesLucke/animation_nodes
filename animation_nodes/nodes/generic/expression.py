import re
import bpy
from bpy.props import *
from ... utils.code import isCodeValid
from ... tree_info import keepNodeState
from ... utils.layout import splitAlignment
from ... events import executionCodeChanged
from ... base_types import AnimationNode

variableNames = list("xyzabcdefghijklmnopqrstuvw")

class ExpressionNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_ExpressionNode"
    bl_label = "Expression"
    bl_width_default = 210
    dynamicLabelType = "HIDDEN_ONLY"

    def settingChanged(self, context = None):
        self.errorMessage = ""
        self.containsSyntaxError = not isCodeValid(self.expression)
        executionCodeChanged()

    def outputDataTypeChanged(self, context):
        self.recreateOutputSocket()

    expression = StringProperty(name = "Expression", update = settingChanged)
    errorMessage = StringProperty()
    lastCorrectionType = IntProperty()
    containsSyntaxError = BoolProperty()

    debugMode = BoolProperty(name = "Debug Mode", default = True,
        description = "Show detailed error messages in the node but is slower.",
        update = executionCodeChanged)

    correctType = BoolProperty(name = "Correct Type", default = True,
        description = "Check the type of the result and correct it if necessary",
        update = executionCodeChanged)

    moduleNames = StringProperty(name = "Modules", default = "math",
        description = "Comma separated module names which can be used inside the expression",
        update = executionCodeChanged,)

    outputDataType = StringProperty(default = "Generic", update = outputDataTypeChanged)

    fixedOutputDataType = BoolProperty(name = "Fixed Data Type", default = False,
        description = "When activated the output type does not automatically changes its type")

    def setup(self):
        self.newInput("Node Control", "New Input")
        self.newOutput("Generic", "Result", "result")

    @keepNodeState
    def recreateOutputSocket(self):
        self.clearOutputs()
        self.newOutput(self.outputDataType, "Result", "result")

    def draw(self, layout):
        row = layout.row(align = True)
        row.prop(self, "expression", text = "")
        self.invokeSocketTypeChooser(row, "changeOutputTypeManually", icon = "SCRIPTWIN")

        col = layout.column(align = True)
        if self.containsSyntaxError:
            col.label("Syntax Error", icon = "ERROR")
        else:
            if self.debugMode and self.expression != "":
                if self.errorMessage != "":
                    row = col.row()
                    row.label(self.errorMessage, icon = "ERROR")
                    self.invokeFunction(row, "clearErrorMessage", icon = "X", emboss = False)
            if self.correctType:
                if self.lastCorrectionType == 1:
                    col.label("Automatic Type Correction", icon = "INFO")
                elif self.lastCorrectionType == 2:
                    col.label("Wrong Output Type", icon = "ERROR")
                    col.label("Expected {}".format(repr(self.outputDataType)), icon = "INFO")

    def drawAdvanced(self, layout):
        layout.prop(self, "moduleNames")

        col = layout.column(align = True)
        col.prop(self, "debugMode")
        col.prop(self, "correctType")

        layout.prop(self, "fixedOutputDataType")

    def drawLabel(self):
        return self.expression

    def drawControlSocket(self, layout, socket):
        left, right = splitAlignment(layout)
        left.label(socket.name)
        self.invokeSocketTypeChooser(right, "newInputSocket", icon = "ZOOMIN", emboss = False)

    @property
    def inputVariables(self):
        return {socket.identifier : socket.text for socket in self.inputs}

    def getExecutionCode(self):
        expression = self.expression.strip()

        if expression == "" or self.containsSyntaxError:
            yield "self.errorMessage = ''"
            yield "result = self.outputs[0].getDefaultValue()"
        elif self.debugMode:
            yield "try:"
            yield "    result = " + expression
            yield "    self.errorMessage = ''"
            yield "except:"
            yield "    result = None"
            yield "    self.errorMessage = str(sys.exc_info()[1])"
        else:
            yield "result = " + expression

        if self.correctType:
            yield "result, self.lastCorrectionType = self.outputs[0].correctValue(result)"

    def getUsedModules(self):
        moduleNames = re.split("\W+", self.moduleNames)
        modules = [module for module in moduleNames if module != ""]
        return ["sys"] + modules

    def clearErrorMessage(self):
        self.errorMessage = ""

    def edit(self):
        self.edit_Inputs()
        self.edit_Output()

    def edit_Inputs(self):
        emptySocket = self.inputs["New Input"]
        directOrigin = emptySocket.directOrigin
        if directOrigin is None: return
        dataOrigin = emptySocket.dataOrigin
        if dataOrigin.dataType == "Node Control": return
        socket = self.newInputSocket(dataOrigin.dataType)
        emptySocket.removeLinks()
        socket.linkWith(directOrigin)

    def edit_Output(self):
        if self.fixedOutputDataType: return
        dataTargets = self.outputs[0].dataTargets
        if len(dataTargets) == 1:
            dataType = dataTargets[0].dataType
            if dataType not in ("Node Control", "Generic", "Generic List"):
                self.changeOutputType(dataType)

    def changeOutputTypeManually(self, dataType):
        self.fixedOutputDataType = True
        self.changeOutputType(dataType)

    def changeOutputType(self, dataType):
        if self.outputDataType != dataType:
            self.outputDataType = dataType

    def newInputSocket(self, dataType):
        name = self.getNewSocketName()
        socket = self.newInput(dataType, name, "input")
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
