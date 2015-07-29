import bpy
from ... mn_node_base import AnimationNode
from ... mn_execution import nodePropertyChanged, nodeTreeChanged, allowCompiling, forbidCompiling
from ... mn_utils import *

defaultVariableNames = list("xyzwabcdefghijklmnopqrstuv")

class mn_ExpressionNode(bpy.types.Node, AnimationNode):
    bl_idname = "mn_ExpressionNode"
    bl_label = "Expression"
    
    expression = bpy.props.StringProperty(default = "x", update = nodeTreeChanged, description = "Python Expression (math module is imported)")
    isExpressionValid = bpy.props.BoolProperty(default = True)
    
    def init(self, context):
        forbidCompiling()
        socket = self.inputs.new("mn_GenericSocket", "x")
        socket.editableCustomName = True
        socket.customName = "x"
        socket.customNameIsVariable = True
        socket.removeable = True
        self.inputs.new("mn_EmptySocket", "...").passiveSocketType = "mn_GenericSocket"
        self.outputs.new("mn_GenericSocket", "Result")
        allowCompiling()
        
    def draw_buttons(self, context, layout):
        layout.prop(self, "expression", text = "")
        if not self.isExpressionValid:
            layout.label("invalid expression", icon = "ERROR")
        
    def update(self):
        forbidCompiling()
        socket = self.inputs.get("...")
        if socket is not None:
            links = socket.links
            if len(links) == 1:
                link = links[0]
                fromSocket = link.from_socket
                self.inputs.remove(socket)
                newSocket = self.inputs.new("mn_GenericSocket", self.getNotUsedSocketName())
                newSocket.editableCustomName = True
                newSocket.customNameIsVariable = True
                newSocket.removeable = True
                newSocket.customName = self.getNextCustomName()
                self.inputs.new("mn_EmptySocket", "...").passiveSocketType = "mn_GenericSocket"
                self.id_data.links.new(newSocket, fromSocket)
        allowCompiling()
        
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
        
    def getInputSocketNames(self):
        inputSocketNames = {}
        for socket in self.inputs:
            if socket.name == "...":
                inputSocketNames["..."] = "EMPTYSOCKET"
            else:
                inputSocketNames[socket.identifier] = socket.customName
        return inputSocketNames
    def getOutputSocketNames(self):
        return {"Result" : "result"}
        
    def useInLineExecution(self):
        return True
    def getModuleList(self):
        return ["math", "re"]
    def getInLineExecutionString(self, outputUse):
        if not isValidCode(self.expression):
            self.isExpressionValid = False
            return "$result$ = None"
        else:
            self.isExpressionValid = True
        
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
        
    def getCustomNames(self):
        customNames = []
        for socket in self.inputs:
            if socket.name != "...":
                customNames.append(socket.customName)
        return customNames
        