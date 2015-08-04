import bpy
from bpy.props import *
from ... events import executionCodeChanged
from ... base_types.node import AnimationNode
from ... utils.names import getRandomString

defaultVariableNames = list("xyzwabcdefghijklmnopqrstuv")

class ExpressionNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_ExpressionNode"
    bl_label = "Expression"

    @property
    def inputNames(self):
        inputSocketNames = {}
        for socket in self.inputs:
            if socket.name == "...":
                inputSocketNames["..."] = "EMPTYSOCKET"
            else:
                inputSocketNames[socket.identifier] = socket.customName
        return inputSocketNames

    outputNames = { "Result" : "result" }

    expression = StringProperty(default = "x", update = executionCodeChanged, description = "Python Expression (math module is imported)")
    isExpressionValid = BoolProperty(default = True)

    def create(self):
        socket = self.inputs.new("an_GenericSocket", "x")
        socket.nameSettings.editable = True
        socket.nameSettings.variable = True
        socket.nameSettings.unique = True
        socket.customName = "x"
        socket.moveable = True
        socket.removeable = True
        self.inputs.new("an_EmptySocket", "...").passiveSocketType = "an_GenericSocket"
        self.outputs.new("an_GenericSocket", "Result")

    def draw_buttons(self, context, layout):
        layout.prop(self, "expression", text = "")
        if not self.isExpressionValid:
            layout.label("invalid expression", icon = "ERROR")

    def edit(self):
        socket = self.inputs.get("...")
        if socket is not None:
            links = socket.links
            if len(links) == 1:
                link = links[0]
                fromSocket = link.from_socket
                self.inputs.remove(socket)
                newSocket = self.inputs.new("an_GenericSocket", self.getNotUsedSocketName())
                newSocket.nameSettings.editable = True
                newSocket.nameSettings.variable = True
                newSocket.nameSettings.unique = True
                newSocket.removeable = True
                newSocket.moveable = True
                newSocket.customName = self.getNextCustomName()
                self.inputs.new("an_EmptySocket", "...").passiveSocketType = "an_GenericSocket"
                self.id_data.links.new(newSocket, fromSocket)

    def getNextCustomName(self):
        for name in defaultVariableNames:
            if not self.isCustomNamesUsed(name): return name
        return getRandomString(5)

    def isCustomNamesUsed(self, customName):
        for socket in self.inputs:
            if socket.customName == customName: return True
        return False

    def getNotUsedSocketName(self):
        socketName = getRandomString(5)
        while self.isSocketNameUsed(socketName):
            socketName = getRandomString(5)
        return socketName
    def isSocketNameUsed(self, name):
        for socket in self.inputs:
            if socket.name == name or socket.identifier == name: return True
        return False

    def getExecutionCode(self):
        self.isExpressionValid = isValidCode(self.expression)
        if not self.isExpressionValid:
            return "$result$ = None"

        expression = self.expression + " "
        customNames = self.getCustomNames()
        codeLine = ""
        currentWord = ""
        for char in expression:
            if char.isalpha():
                currentWord += char
            else:
                if currentWord in customNames:
                    currentWord = "%" + currentWord + "%"
                codeLine += currentWord
                currentWord = ""
                codeLine += char
        return "try: $result$ = " + codeLine + "\nexcept: $result$ = None"

    def getModuleList(self):
        return ["math", "re"]

    def getCustomNames(self):
        customNames = []
        for socket in self.inputs:
            if socket.name != "...":
                customNames.append(socket.customName)
        return customNames

def isValidCode(code):
    try:
        ast.parse(code)
    except SyntaxError:
        return False
    return True
