import bpy
from bpy.types import Node
from mn_node_base import AnimationNode
from mn_execution import nodePropertyChanged, allowCompiling, forbidCompiling

class mn_ObjectMeshInfo(Node, AnimationNode):
	bl_idname = "mn_ObjectMeshInfo"
	bl_label = "Object Mesh Info"
	
	def init(self, context):
		forbidCompiling()
		self.inputs.new("mn_ObjectSocket", "Object").showName = False
		self.outputs.new("mn_VertexListSocket", "Vertices")
		allowCompiling()
		
	def getInputSocketNames(self):
		return {"Object" : "object"}
	def getOutputSocketNames(self):
		return {"Vertices" : "vertices"}
		
	def useInLineExecution(self):
		return True
	def getInLineExecutionString(self, outputUse):
		codeLines = []
		codeLines.append("$vertices$ = []")
		codeLines.append("try:")
		codeLines.append("    for vertex in %object%.data.vertices:")
		codeLines.append("        $vertices$.append([vertex.co, vertex.normal])")
		codeLines.append("except:")
		codeLines.append("    pass")
		return "\n".join(codeLines)
		