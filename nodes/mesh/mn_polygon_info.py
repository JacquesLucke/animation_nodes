import bpy
from bpy.types import Node
from animation_nodes.mn_node_base import AnimationNode
from animation_nodes.mn_execution import nodePropertyChanged, allowCompiling, forbidCompiling
from animation_nodes.utils.mn_mesh_utils import *

class mn_PolygonInfo(Node, AnimationNode):
	bl_idname = "mn_PolygonInfo"
	bl_label = "Polygon Info"
	
	def init(self, context):
		forbidCompiling()
		self.inputs.new("mn_PolygonSocket", "Polygon")
		self.outputs.new("mn_VectorSocket", "Center")
		self.outputs.new("mn_VectorSocket", "Normal")
		self.outputs.new("mn_VectorSocket", "Material Index")
		self.outputs.new("mn_FloatSocket", "Area")
		allowCompiling()
		
	def getInputSocketNames(self):
		return {"Polygon" : "polygon"}
	def getOutputSocketNames(self):
		return {"Center" : "center",
				"Normal" : "normal",
				"Material Index" : "materialIndex",
				"Area" : "area"}
		
	def execute(self, polygon):
		return polygon.center, polygon.normal, polygon.materialIndex, polygon.area