import re
import bpy
import ast
from bpy.props import *
from ... sockets.info import toIdName
from ... events import executionCodeChanged
from ... base_types.node import AnimationNode

variableNames = list("xyzabcdefghijklmnopqrstuvw")

class ExpressionNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_ExpressionNode"
    bl_label = "Expression"

    def settingChanged(self, context = None):
        self.executionError = ""
        self.containsSyntaxError = not isExpressionValid(self.expression)
        executionCodeChanged()

    expression = StringProperty(name = "Expression", update = settingChanged)
    containsSyntaxError = BoolProperty()
    executionError = StringProperty()

    moduleNames = StringProperty(name = "Modules", update = executionCodeChanged,
        description = "Comma separated module names which can be used inside the expression")

    def create(self):
        self.width = 200
        self.inputs.new("an_NodeControlSocket", "New Input")
        self.outputs.new("an_GenericSocket", "Result", "result")

    def draw(self, layout):
        layout.prop(self, "expression", text = "")
        if self.containsSyntaxError:
            layout.label("Syntax Error", icon = "ERROR")
        if self.executionError != "":
            row = layout.row()
            row.label(self.executionError, icon = "ERROR")
            self.invokeFunction(row, "clearErrorMessage", icon = "X", emboss = False)

    def drawAdvanced(self, layout):
        layout.prop(self, "moduleNames")

    def drawControlSocket(self, layout, socket):
        row = layout.row()
        row.alignment = "LEFT"
        self.invokeFunction(row, "chooseNewInputType", text = "New Input", emboss = False)

    def chooseNewInputType(self):
        self.chooseSocketDataType("newInputSocket")

    @property
    def inputVariables(self):
        return {socket.identifier : socket.text for socket in self.inputs}

    def getExecutionCode(self):
        expression = self.expression.strip()
        if expression == "" or self.containsSyntaxError: return "result = None"

        lines = []
        lines.append("try: result = " + expression)
        lines.append("except:")
        lines.append("    result = None")
        lines.append("    self.executionError = str(sys.exc_info()[1])")
        return lines

    def getModuleList(self):
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
        socket = self.inputs.new(toIdName(dataType), name, "input")
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

def isExpressionValid(expression):
    try:
        ast.parse(expression)
        return True
    except SyntaxError:
        return False
