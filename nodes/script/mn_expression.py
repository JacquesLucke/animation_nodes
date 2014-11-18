import bpy, ast
from bpy.types import Node
from animation_nodes.mn_node_base import AnimationNode
from animation_nodes.mn_execution import nodePropertyChanged, nodeTreeChanged, allowCompiling, forbidCompiling
from animation_nodes.mn_utils import *

defaultVariableNames = list("abcdefghijklmnopqrstuvwxyz")

class mn_ExpressionNode(Node, AnimationNode):
	bl_idname = "mn_ExpressionNode"
	bl_label = "Expression"
	
	expression = bpy.props.StringProperty(default = "a+b", update = nodeTreeChanged, description = "Python Expression (math module is imported)")
	isExpressionValid = bpy.props.BoolProperty(default = True)
	
	def init(self, context):
		forbidCompiling()
		aSocket = self.inputs.new("mn_GenericSocket", "a")
		aSocket.editableCustomName = True
		aSocket.customName = "a"
		aSocket.customNameIsVariable = True
		aSocket.removeable = True
		bSocket = self.inputs.new("mn_GenericSocket", "b")
		bSocket.editableCustomName = True
		bSocket.customName = "b"
		bSocket.customNameIsVariable = True
		bSocket.removeable = True
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
		return ["math"]
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
		
def isValidCode(code):
	try:
		ast.parse(code)
	except SyntaxError:
		return False
	return True

