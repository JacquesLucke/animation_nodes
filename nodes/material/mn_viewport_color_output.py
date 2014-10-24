import bpy, random
from bpy.types import Node
from mn_cache import getUniformRandom
from mn_node_base import AnimationNode
from mn_execution import nodePropertyChanged, allowCompiling, forbidCompiling

class mn_ViewportColorNode(Node, AnimationNode):
	bl_idname = "mn_ViewportColorNode"
	bl_label = "Viewport Color"
	
	materialName = bpy.props.StringProperty(update = nodePropertyChanged)
	
	def init(self, context):
		forbidCompiling()
		self.inputs.new("mn_ColorSocket", "Color")
		allowCompiling()
		
	def draw_buttons(self, context, layout):
		layout.prop_search(self, 'materialName', bpy.data, 'materials', text='', icon='MATERIAL_DATA')
		
	def getInputSocketNames(self):
		return {"Color" : "color"}
	def getOutputSocketNames(self):
		return {}
		
	def execute(self, color):
		material = bpy.data.materials.get(self.materialName)
		if material is not None:
			try:
				material.diffuse_color = color[:3]
			except: pass
		return None
		