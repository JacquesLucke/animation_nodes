import bpy
from bpy.types import Node
from animation_nodes.mn_node_base import AnimationNode
from animation_nodes.mn_execution import nodePropertyChanged, allowCompiling, forbidCompiling

class mn_IntegerInputNode(Node, AnimationNode):
	bl_idname = "mn_IntegerInputNode"
	bl_label = "Integer Input"
	isDetermined = True
	
	def init(self, context):
		forbidCompiling()
		self.inputs.new("mn_IntegerSocket", "Number")
		self.outputs.new("mn_IntegerSocket", "Number")
		allowCompiling()
		
	def getInputSocketNames(self):
		return {"Number" : "number"}
	def getOutputSocketNames(self):
		return {"Number" : "number"}
		
	def execute(self, number):
		return number

classes = [
	mn_IntegerInputNode
]
    
def register():
    for cls in classes:
        bpy.utils.register_class(cls)
 
 
def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
