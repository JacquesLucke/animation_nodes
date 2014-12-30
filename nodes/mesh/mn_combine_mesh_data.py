import bpy, time
from bpy.types import Node
from animation_nodes.mn_node_base import AnimationNode
from animation_nodes.mn_execution import nodePropertyChanged, allowCompiling, forbidCompiling
from animation_nodes.utils.mn_mesh_utils import *
from animation_nodes.mn_cache import *

class mn_CombineMeshData(Node, AnimationNode):
	bl_idname = "mn_CombineMeshData"
	bl_label = "Combine Mesh Data"
	
	def init(self, context):
		forbidCompiling()
		self.inputs.new("mn_VectorListSocket", "Vertex Locations")
		self.inputs.new("mn_EdgeIndicesList", "Edges Indices")
		self.inputs.new("mn_PolygonIndicesList", "Polygons Indices")
		self.outputs.new("mn_MeshDataSocket", "Mesh Data")	
		allowCompiling()
		
	def draw_buttons(self, context, layout):
		pass
		
	def getInputSocketNames(self):
		return {"Vertex Locations" : "vertexLocations",
				"Edges Indices" : "edgesIndices",
				"Polygons Indices" : "polygonsIndices"}	
				
	def getOutputSocketNames(self):
		return {"Mesh Data" : "meshData"}
	
		
	def execute(self, vertexLocations, edgesIndices, polygonsIndices):	
		return MeshData(vertexLocations, edgesIndices, polygonsIndices)
