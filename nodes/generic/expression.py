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

    def create(self):
        self.width = 200
        socket = self.inputs.new("an_EmptySocket", "New Input", "empty")
        socket.socketGroup = "ALL"
        socket.newSocketCallbackName = "newInputSocket"
        socket.display.margin = 1
        self.outputs.new("an_GenericSocket", "Result", "result")

    def draw(self, layout):
        layout.prop(self, "expression", text = "")
        if self.containsSyntaxError:
            layout.label("Syntax Error", icon = "ERROR")
        if self.executionError != "":
            layout.label(self.executionError, icon = "ERROR")

    @property
    def inputNames(self):
        return {socket.identifier : socket.customName for socket in self.inputs}

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
        return ["sys"]

    def edit(self):
        emptySocket = self.inputs["New Input"]
        directOrigin = emptySocket.directOriginSocket
        if directOrigin is None: return
        dataOrigin = emptySocket.dataOriginSocket
        if dataOrigin.dataType == "Empty": return
        socket = self.newInputSocket(dataOrigin.dataType)
        emptySocket.removeConnectedLinks()
        socket.linkWith(directOrigin)

    def newInputSocket(self, dataType):
        name = self.getNewSocketName()
        socket = self.inputs.new(toIdName(dataType), name, "input")
        socket.nameSettings.editable = True
        socket.nameSettings.variable = True
        socket.nameSettings.unique = True
        socket.displayCustomName = True
        socket.display.customNameInput = True
        socket.customName = name
        socket.moveable = True
        socket.removeable = True
        socket.moveUp()
        return socket

    def getNewSocketName(self):
        inputs = self.inputsByCustomName
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
