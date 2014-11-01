import bpy
from bpy.types import Node
from mn_node_base import AnimationNode
from mn_execution import nodePropertyChanged, nodeTreeChanged, allowCompiling, forbidCompiling
from mn_utils import *

types = ["Float", "Integer", "String"]

typeItems = []
for type in types:
	typeItems.append((type, type, ""))

class mn_ConvertNode(Node, AnimationNode):
	bl_idname = "mn_ConvertNode"
	bl_label = "Convert"
	
	convertType = bpy.props.EnumProperty(items = typeItems, default = "Integer")
	
	def init(self, context):
		forbidCompiling()
		self.inputs.new("mn_GenericSocket", "Old")
		self.buildOutputSocket()
		allowCompiling()
		
	def update(self):
		forbidCompiling()
		socket = self.outputs.get("New")
		if socket is not None:
			links = socket.links
			if len(links) == 1:
				link = links[0]
				toSocket = link.to_socket
				if toSocket.node.type != "REROUTE":
					if socket.dataType != toSocket.dataType:
						if toSocket.dataType in types:
							self.convertType = toSocket.dataType
							self.buildOutputSocket()
					
		allowCompiling()
		
	def buildOutputSocket(self):
		forbidCompiling()
		connections = getConnectionDictionaries(self)
		self.outputs.clear()
		if self.convertType == "Float": self.outputs.new("mn_FloatSocket", "New")
		if self.convertType == "Integer": self.outputs.new("mn_IntegerSocket", "New")
		if self.convertType == "String": self.outputs.new("mn_StringSocket", "New")
		tryToSetConnectionDictionaries(self, connections)
		allowCompiling()
		
	def getInputSocketNames(self):
		return {"Old" : "old"}
	def getOutputSocketNames(self):
		return {"New" : "new"}
		
	def useInLineExecution(self):
		return True
	def getInLineExecutionString(self, outputUse):
		t = self.convertType
		if t == "Float": return '''
try: $new$ = float(%old%)
except: $new$ = 0
'''
		elif t == "Integer": return '''
try: $new$ = int(%old%)
except: $new$ = 0
'''
		elif t == "String": return '''
try: $new$ = str(%old%)
except: $new$ = 0
'''