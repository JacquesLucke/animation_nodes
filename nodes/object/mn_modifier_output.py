import bpy
from bpy.types import Node
from mn_node_base import AnimationNode
from mn_execution import nodePropertyChanged, nodeTreeChanged, allowCompiling, forbidCompiling

class mn_ModifierOutputNode(Node, AnimationNode):
	bl_idname = "mn_ModifierOutputNode"
	bl_label = "Modifier Output"
	
	def init(self, context):
		forbidCompiling()
		objectSocket = self.inputs.new("mn_ObjectSocket", "Object")
		objectSocket.showName = True
		self.inputs.new("mn_StringSocket", "Path")
		self.inputs.new("mn_GenericSocket", "Data")
		allowCompiling()
		
	def getInputSocketNames(self):
		return {"Object" : "object",
				"Path" : "dataPath",
				"Data" : "data"}
	def getOutputSocketNames(self):
		return {}
		
	def execute(self, object, dataPath, data):
		try: exec("object." + dataPath + " = data")
		except:	pass
		return None