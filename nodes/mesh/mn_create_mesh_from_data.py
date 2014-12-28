import bpy, bmesh
from bpy.types import Node
from animation_nodes.mn_node_base import AnimationNode
from animation_nodes.mn_execution import nodePropertyChanged, nodeTreeChanged, allowCompiling, forbidCompiling
from animation_nodes.utils.mn_mesh_utils import *
import bmesh

creation_type_items = [
	("POLYGONS", "Polygons", ""),
	("VERTICES_ONLY", "Vertices only", "") ]

class mn_CreateMeshFromData(Node, AnimationNode):
	bl_idname = "mn_CreateMeshFromData"
	bl_label = "Create Mesh"
	
	def selectedTypeChanged(self, context):
		self.changeHideStatusOfSockets()
	
	creation_type = bpy.props.EnumProperty(items = creation_type_items, name = "Creation Type", update = selectedTypeChanged)
	
	def init(self, context):
		forbidCompiling()
		self.inputs.new("mn_PolygonListSocket", "Polygons")
		self.inputs.new("mn_VertexListSocket", "Vertices")
		self.changeHideStatusOfSockets()
		self.outputs.new("mn_MeshSocket", "Mesh")
		allowCompiling()
		
	def draw_buttons(self, context, layout):
		row = layout.row(align = True)
		row.prop(self, "creation_type")
		
	def getInputSocketNames(self):
		return {"Polygons" : "polygons",
				"Vertices" : "vertices"}
	def getOutputSocketNames(self):
		return {"Mesh" : "mesh"}
		
	def execute(self, polygons, vertices):
		if self.creation_type == "POLYGONS":
			return getBMeshFromPolygons(polygons)
		if self.creation_type == "VERTICES_ONLY":
			return getBMeshFromVertices(vertices)
		return bmesh.new()
		
	def changeHideStatusOfSockets(self):
		self.inputs["Polygons"].hide = True
		self.inputs["Vertices"].hide = True
		
		if self.creation_type == "POLYGONS":
			self.inputs["Polygons"].hide = False
		if self.creation_type == "VERTICES_ONLY":
			self.inputs["Vertices"].hide = False