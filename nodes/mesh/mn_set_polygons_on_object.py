import bpy
from bpy.types import Node
from animation_nodes.mn_node_base import AnimationNode
from animation_nodes.mn_execution import nodePropertyChanged, allowCompiling, forbidCompiling
from animation_nodes.utils.mn_mesh_utils import *
import bmesh

class mn_SetPolygonsOnObject(Node, AnimationNode):
	bl_idname = "mn_SetPolygonsOnObject"
	bl_label = "Set Mesh"
	
	def init(self, context):
		forbidCompiling()
		self.inputs.new("mn_ObjectSocket", "Object").showName = False
		self.inputs.new("mn_PolygonListSocket", "Polygons")
		self.outputs.new("mn_ObjectSocket", "Object")
		allowCompiling()
		
	def getInputSocketNames(self):
		return {"Object" : "object",
				"Polygons" : "polygons"}
	def getOutputSocketNames(self):
		return {"Object" : "object"}
		
	def execute(self, object, polygons):
		if object is None: return object
		if object.type != "MESH": return object
		replace_mesh_by_polygons(object.data, polygons)
		return object