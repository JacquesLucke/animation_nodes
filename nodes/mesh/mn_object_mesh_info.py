import bpy
from bpy.types import Node
from animation_nodes.mn_node_base import AnimationNode
from animation_nodes.mn_execution import nodePropertyChanged, allowCompiling, forbidCompiling
from animation_nodes.utils.mn_mesh_utils import *

class mn_ObjectMeshInfo(Node, AnimationNode):
	bl_idname = "mn_ObjectMeshInfo"
	bl_label = "Object Mesh Info"
	
	def init(self, context):
		forbidCompiling()
		self.inputs.new("mn_ObjectSocket", "Object").showName = False
		self.outputs.new("mn_PolygonListSocket", "Polygons")
		self.outputs.new("mn_VertexListSocket", "Vertices")
		allowCompiling()
		
	def getInputSocketNames(self):
		return {"Object" : "object"}
	def getOutputSocketNames(self):
		return {"Polygons" : "polygons",
				"Vertices" : "vertices"}
		
	def execute(self, object):
		if object is None: return [], []
		if object.type != "MESH": return [], []
		return getPolygonsFromMesh(object.data), getVerticesFromMesh(object.data)
		

