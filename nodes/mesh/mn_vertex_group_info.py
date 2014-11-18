import bpy
from bpy.types import Node
from animation_nodes.mn_node_base import AnimationNode
from animation_nodes.mn_execution import nodePropertyChanged, allowCompiling, forbidCompiling

class mn_VertexGroupInfo(Node, AnimationNode):
	bl_idname = "mn_VertexGroupInfo"
	bl_label = "Vertex Group Info"
	
	def init(self, context):
		forbidCompiling()
		self.inputs.new("mn_ObjectSocket", "Object").showName = False
		self.inputs.new("mn_IntegerSocket", "Group Index").number = 0
		socket = self.inputs.new("mn_FloatSocket", "Weight Min")
		socket.number = 1.0
		socket.setMinMax(0.0, 1.0)
		socket = self.inputs.new("mn_FloatSocket", "Weight Max")
		socket.number = 1.0
		socket.setMinMax(0.0, 1.0)
		self.outputs.new("mn_VertexListSocket", "Vertices")
		allowCompiling()
		
	def getInputSocketNames(self):
		return {"Object" : "object",
				"Group Index" : "index",
				"Weight Min" : "min",
				"Weight Max" : "max"}
	def getOutputSocketNames(self):
		return {"Vertices" : "vertices"}
		
	def useInLineExecution(self):
		return True
	def getInLineExecutionString(self, outputUse):
		codeLines = []
		codeLines.append("$vertices$ = []")
		codeLines.append("try:")
		codeLines.append("    vertexGroup = %object%.vertex_groups[%index%]")
		codeLines.append("    for vertex in %object%.data.vertices:")
		codeLines.append("        if %min% <= vertexGroup.weight(vertex.index) <= %max%:")
		codeLines.append("            $vertices$.append([vertex.co, vertex.normal, %object%])")
		codeLines.append("except: pass")
		return "\n".join(codeLines)
		
