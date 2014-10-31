import bpy
from bpy.types import Node
from mn_node_base import AnimationNode
from mn_execution import nodePropertyChanged, nodeTreeChanged, allowCompiling, forbidCompiling

types = ["Float", "Integer", "String"]

typeItems = []
for type in types:
	typeItems.append((type, type, ""))

class mn_ConvertNode(Node, AnimationNode):
	bl_idname = "mn_ConvertNode"
	bl_label = "Convert"
	
	def convertTypeChanged(self, context):
		self.buildOutputSocket()
		nodeTreeChanged()
	
	convertType = bpy.props.EnumProperty(items = typeItems, update = convertTypeChanged, default = "Integer")
	
	def init(self, context):
		forbidCompiling()
		self.inputs.new("mn_GenericSocket", "Old")
		self.outputs.new("mn_IntegerSocket", "New")
		allowCompiling()
		
	def draw_buttons_ext(self, context, layout):
		layout.prop(self, "convertType", text = "Type")
		
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
						self.id_data.links.remove(link)
						if toSocket.dataType in types:
							self.convertType = toSocket.dataType
							self.buildOutputSocket()
							self.id_data.links.new(toSocket, self.outputs.get("New"))
					
		allowCompiling()
		
	def buildOutputSocket(self):
		forbidCompiling()
		self.outputs.clear()
		if self.convertType == "Float": self.outputs.new("mn_FloatSocket", "New")
		if self.convertType == "Integer": self.outputs.new("mn_IntegerSocket", "New")
		if self.convertType == "String": self.outputs.new("mn_StringSocket", "New")
		allowCompiling()
		
	def getInputSocketNames(self):
		return {"Old" : "old"}
	def getOutputSocketNames(self):
		return {"New" : "new"}
		
	def useInLineExecution(self):
		return True
	def getInLineExecutionString(self, outputUse):
		return '''
try: $new$ = int(%old%)
except: $new$ = 0
'''