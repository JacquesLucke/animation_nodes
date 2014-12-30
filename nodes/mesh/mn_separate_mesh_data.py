import bpy, time
from bpy.types import Node
from animation_nodes.mn_node_base import AnimationNode
from animation_nodes.mn_execution import nodePropertyChanged, allowCompiling, forbidCompiling
from animation_nodes.utils.mn_mesh_utils import *
from animation_nodes.mn_cache import *

class mn_SeparateMeshData(Node, AnimationNode):
	bl_idname = "mn_SeparateMeshData"
	bl_label = "Separate Mesh Data"
	
	def init(self, context):
		forbidCompiling()
		self.inputs.new("mn_MeshDataSocket", "Mesh Data")
		self.outputs.new("mn_VectorListSocket", "Vertex Locations")
		self.outputs.new("mn_EdgeIndicesList", "Edges Indices")
		self.outputs.new("mn_PolygonIndicesList", "Polygons Indices")
		allowCompiling()
		
	def draw_buttons(self, context, layout):
		pass
		
	def getInputSocketNames(self):
		return {"Mesh Data" : "meshData"}
	def getOutputSocketNames(self):
		return {"Vertex Locations" : "vertexLocations",
				"Edges Indices" : "edgesIndices",
				"Polygons Indices" : "polygonsIndices"}
		
	def execute(self, meshData):	
		return meshData.vertices, meshData.edges, meshData.polygons
