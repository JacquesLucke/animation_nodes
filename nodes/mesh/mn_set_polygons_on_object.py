import bpy, bmesh
from bpy.types import Node
from animation_nodes.mn_node_base import AnimationNode
from animation_nodes.mn_execution import nodePropertyChanged, allowCompiling, forbidCompiling
from animation_nodes.utils.mn_mesh_utils import *
import bmesh

class mn_SetPolygonsOnObject(Node, AnimationNode):
	bl_idname = "mn_SetPolygonsOnObject"
	bl_label = "Set Mesh"
	
	calculateNormals = bpy.props.BoolProperty(name = "Calculate Normals", default = False)
	removeDoubles = bpy.props.BoolProperty(name = "Remove Doubles", default = False)
	
	def init(self, context):
		forbidCompiling()
		self.inputs.new("mn_ObjectSocket", "Object").showName = False
		self.inputs.new("mn_PolygonListSocket", "Polygons")
		self.outputs.new("mn_ObjectSocket", "Object")
		allowCompiling()
		
	def draw_buttons(self, context, layout):
		layout.prop(self, "calculateNormals")
		layout.prop(self, "removeDoubles")
		
	def getInputSocketNames(self):
		return {"Object" : "object",
				"Polygons" : "polygons"}
	def getOutputSocketNames(self):
		return {"Object" : "object"}
		
	def execute(self, object, polygons):
		if object is None: return object
		if object.type != "MESH": return object
		bm = getBmeshFromPolygons(polygons)
		if self.removeDoubles:
			bmesh.ops.remove_doubles(bm, verts = bm.verts, dist = 0.0001)
		if self.calculateNormals:
			bmesh.ops.recalc_face_normals(bm, faces = bm.faces)
		bm.to_mesh(object.data)
		bm.free()
		return object