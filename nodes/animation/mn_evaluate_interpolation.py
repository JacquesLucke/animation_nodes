import bpy
from bpy.types import Node
from animation_nodes.mn_node_base import AnimationNode
from animation_nodes.mn_execution import nodePropertyChanged, allowCompiling, forbidCompiling

class mn_EvaluateInterpolation(Node, AnimationNode):
	bl_idname = "mn_EvaluateInterpolation"
	bl_label = "Evaluate Interpolation"
	isDetermined = True
	
	def init(self, context):
		forbidCompiling()
		self.inputs.new("mn_InterpolationSocket", "Interpolation").showName = False
		self.inputs.new("mn_FloatSocket", "Position").setMinMax(0, 1)
		self.outputs.new("mn_FloatSocket", "Value")
		allowCompiling()
		
	def getInputSocketNames(self):
		return {"Interpolation" : "interpolation", "Position" : "position"}
	def getOutputSocketNames(self):
		return {"Value" : "value"}
		
	def execute(self, interpolation, position):
		return interpolation[0](max(min(position, 1.0), 0.0), interpolation[1])

classes = [
	mn_EvaluateInterpolation
]
    
def register():
    for cls in classes:
        bpy.utils.register_class(cls)
 
 
def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
