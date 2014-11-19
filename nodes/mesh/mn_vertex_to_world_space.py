import bpy
from bpy.types import Node
from animation_nodes.mn_node_base import AnimationNode
from animation_nodes.mn_execution import nodePropertyChanged, allowCompiling, forbidCompiling

class mn_VertexToWorldSpace(Node, AnimationNode):
	bl_idname = "mn_VertexToWorldSpace"
	bl_label = "Vertex To World Space"
	isDetermined = True
	
	def init(self, context):
		forbidCompiling()
		self.inputs.new("mn_VertexSocket", "Vertex")
		self.outputs.new("mn_VertexSocket", "Vertex")
		allowCompiling()
		
	def getInputSocketNames(self):
		return {"Vertex" : "vertex"}
	def getOutputSocketNames(self):
		return {"Vertex" : "vertex"}
		
	def useInLineExecution(self):
		return True
	def getInLineExecutionString(self, outputUse):
		codeLines = []
		codeLines.append("$vertex$ = %vertex%")
		codeLines.append("try:")
		codeLines.append("    worldMatrix = $vertex$[3].matrix_world")
		codeLines.append("    $vertex$[0] = worldMatrix * $vertex$[0]")
		codeLines.append("    $vertex$[1] = worldMatrix * $vertex$[1]")
		codeLines.append("except: pass")
		return "\n".join(codeLines)
		