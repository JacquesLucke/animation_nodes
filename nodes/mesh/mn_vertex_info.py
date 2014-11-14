import bpy
from bpy.types import Node
from mn_node_base import AnimationNode
from mn_execution import nodePropertyChanged, allowCompiling, forbidCompiling

class mn_VertexInfo(Node, AnimationNode):
	bl_idname = "mn_VertexInfo"
	bl_label = "Vertex Info"
	isDetermined = True
	
	def init(self, context):
		forbidCompiling()
		self.inputs.new("mn_VertexSocket", "Vertex")
		self.outputs.new("mn_VectorSocket", "Position")
		self.outputs.new("mn_VectorSocket", "Normal")
		allowCompiling()
		
	def getInputSocketNames(self):
		return {"Vertex" : "vertex"}
	def getOutputSocketNames(self):
		return {"Position" : "position",
				"Normal" : "normal"}
		
	def useInLineExecution(self):
		return True
	def getInLineExecutionString(self, outputUse):
		codeLines = []
		if outputUse["Position"]: codeLines.append("$position$ = %vertex%[0]")
		if outputUse["Normal"]: codeLines.append("$normal$ = %vertex%[1]")
		return "\n".join(codeLines)
		