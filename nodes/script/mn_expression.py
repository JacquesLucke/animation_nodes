import bpy, ast
from bpy.types import Node
from mn_node_base import AnimationNode
from mn_execution import nodePropertyChanged, nodeTreeChanged, allowCompiling, forbidCompiling
from mn_utils import * 

class mn_ExpressionNode(Node, AnimationNode):
	bl_idname = "mn_ExpressionNode"
	bl_label = "Expression"
	
	expression = bpy.props.StringProperty(default = "a+bw", update = nodeTreeChanged, description = "Python Expression")
	
	def init(self, context):
		forbidCompiling()
		aSocket = self.inputs.new("mn_GenericSocket", "a")
		aSocket.editableCustomName = True
		aSocket.customName = "a"
		aSocket.customNameIsVariable = True
		aSocket.removeableSocket = True
		bSocket = self.inputs.new("mn_GenericSocket", "b")
		bSocket.editableCustomName = True
		bSocket.customName = "bw"
		bSocket.customNameIsVariable = True
		bSocket.removeableSocket = True
		self.inputs.new("mn_EmptySocket", "...")
		self.outputs.new("mn_GenericSocket", "Result")
		allowCompiling()
		
	def draw_buttons(self, context, layout):
		layout.prop(self, "expression", text = "")
		
	def update(self):
		forbidCompiling()
		socket = self.inputs.get("...")
		if socket is not None:
			links = socket.links
			if len(links) == 1:
				link = links[0]
				fromSocket = link.from_socket
				self.inputs.remove(socket)
				newSocketName = "expression socket" + getRandomString(5)
				newSocket = self.inputs.new("mn_GenericSocket", newSocketName)
				newSocket.editableCustomName = True
				newSocket.customNameIsVariable = True
				newSocket.removeableSocket = True
				newSocket.customName = getRandomString(1)
				self.inputs.new("mn_EmptySocket", "...")
				self.id_data.links.new(newSocket, fromSocket)	
		allowCompiling()
		
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
		if not isValidCode(self.expression): return "$result$ = None"
		
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