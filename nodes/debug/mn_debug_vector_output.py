import bpy
from bpy.types import Node
from animation_nodes.mn_node_base import AnimationNode
from animation_nodes.mn_execution import nodePropertyChanged, allowCompiling, forbidCompiling

class mn_DebugVectorOutputNode(Node, AnimationNode):
	bl_idname = "mn_DebugVectorOutputNode"
	bl_label = "Debug Vector Output"
	
	debugOutputString_component0 = bpy.props.StringProperty(default = "")
	debugOutputString_component1 = bpy.props.StringProperty(default = "")
	debugOutputString_component2 = bpy.props.StringProperty(default = "")
	
	def init(self, context):
		forbidCompiling()
		self.inputs.new("mn_VectorSocket", "Vector")
		allowCompiling()
		
	def draw_buttons(self, context, layout):
		layout.label(self.debugOutputString_component0)
		layout.label(self.debugOutputString_component1)
		layout.label(self.debugOutputString_component2)
		
	def execute(self, input):
		self.debugOutputString_component0 = "X: "+str(round(input["Vector"][0], 2))
		self.debugOutputString_component1 = "Y: "+str(round(input["Vector"][1], 2))
		self.debugOutputString_component2 = "Z: "+str(round(input["Vector"][2], 2))
		return {}


classes = [
	mn_DebugVectorOutputNode
]
    
def register():
    for cls in classes:
        bpy.utils.register_class(cls)
 
 
def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
