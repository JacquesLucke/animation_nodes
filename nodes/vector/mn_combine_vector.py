import bpy
from bpy.types import Node
from animation_nodes.mn_node_base import AnimationNode
from animation_nodes.mn_execution import nodePropertyChanged, nodeTreeChanged, allowCompiling, forbidCompiling

class mn_CombineVector(Node, AnimationNode):
	bl_idname = "mn_CombineVector"
	bl_label = "Combine Vector"
	isDetermined = True
	
	def init(self, context):
		forbidCompiling()
		self.inputs.new("mn_FloatSocket", "X")
		self.inputs.new("mn_FloatSocket", "Y")
		self.inputs.new("mn_FloatSocket", "Z")
		self.outputs.new("mn_VectorSocket", "Vector")
		allowCompiling()
		
	def getInputSocketNames(self):
		return {"X" : "x",
				"Y" : "y",
				"Z" : "z"}
	def getOutputSocketNames(self):
		return {"Vector" : "vector"}

	def useInLineExecution(self):
		return True
	def getInLineExecutionString(self, outputUse):
		return "$vector$ = [%x%, %y%, %z%]"

classes = [
	mn_CombineVector
]
    
def register():
    for cls in classes:
        bpy.utils.register_class(cls)
 
 
def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
