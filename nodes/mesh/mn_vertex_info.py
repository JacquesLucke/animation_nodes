import bpy
from bpy.types import Node
from animation_nodes.mn_node_base import AnimationNode
from animation_nodes.mn_execution import nodePropertyChanged, allowCompiling, forbidCompiling

class mn_VertexInfo(Node, AnimationNode):
	bl_idname = "mn_VertexInfo"
	bl_label = "Vertex Info"
	isDetermined = True
	
	def init(self, context):
		forbidCompiling()
		self.inputs.new("mn_VertexSocket", "Vertex")
		self.outputs.new("mn_VectorSocket", "Position")
		self.outputs.new("mn_VectorSocket", "Normal")
		self.outputs.new("mn_ObjectSocket", "From Object")
		allowCompiling()
		
	def getInputSocketNames(self):
		return {"Vertex" : "vertex"}
	def getOutputSocketNames(self):
		return {"Position" : "position",
				"Normal" : "normal",
				"From Object" : "fromObject"}
		
	def useInLineExecution(self):
		return True
	def getInLineExecutionString(self, outputUse):
		codeLines = []
		if outputUse["Position"]: codeLines.append("$position$ = %vertex%[0]")
		if outputUse["Normal"]: codeLines.append("$normal$ = %vertex%[1]")
		if outputUse["From Object"]: codeLines.append("$fromObject$ = %vertex%[2]")
		return "\n".join(codeLines)
		

classes = [
	mn_VertexInfo
]
    
def register():
    for cls in classes:
        bpy.utils.register_class(cls)
 
 
def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
