import bpy, bmesh
from bpy.types import Node
from animation_nodes.mn_node_base import AnimationNode
from animation_nodes.mn_execution import nodePropertyChanged, nodeTreeChanged, allowCompiling, forbidCompiling
from animation_nodes.utils.mn_mesh_utils import *
import bmesh

creation_type_items = [
	("POLYGONS_ONLY", "Polygons only", ""),
	("NORMAL", "Vertices and Indices", "") ]

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
		self.inputs.new("mn_IntegerList2DSocket", "Edges Indices")
		self.inputs.new("mn_IntegerList2DSocket", "Polygons Indices")
		self.changeHideStatusOfSockets()
		self.outputs.new("mn_MeshSocket", "Mesh")
		allowCompiling()
		
	def draw_buttons(self, context, layout):
		layout.prop(self, "creation_type")
		
	def getInputSocketNames(self):
		return {"Polygons" : "polygons",
				"Vertices" : "vertices",
				"Edges Indices" : "edgesIndices",
				"Polygons Indices" : "polygonsIndices"}
	def getOutputSocketNames(self):
		return {"Mesh" : "mesh"}
		
	def execute(self, polygons, vertices, edgesIndices, polygonsIndices):
		if self.creation_type == "POLYGONS_ONLY":
			return getBMeshFromPolygons(polygons)
		if self.creation_type == "NORMAL":
			return getBMeshFromVerticesAndIndices(vertices, edgesIndices, polygonsIndices)
		return bmesh.new()
		
	def changeHideStatusOfSockets(self):
		self.inputs["Polygons"].hide = True
		self.inputs["Vertices"].hide = True
		self.inputs["Edges Indices"].hide = True
		self.inputs["Polygons Indices"].hide = True
		
		if self.creation_type == "POLYGONS_ONLY":
			self.inputs["Polygons"].hide = False
		if self.creation_type == "NORMAL":
			self.inputs["Vertices"].hide = False
			self.inputs["Edges Indices"].hide = False
			self.inputs["Polygons Indices"].hide = False