import bpy
from bpy.types import Node
from animation_nodes.mn_node_base import AnimationNode
from animation_nodes.mn_execution import nodePropertyChanged, allowCompiling, forbidCompiling
from animation_nodes.utils.mn_mesh_utils import *
from mathutils import Matrix

class mn_TransformPolygon(Node, AnimationNode):
	bl_idname = "mn_TransformPolygon"
	bl_label = "Transform Polygon"
	
	def init(self, context):
		forbidCompiling()
		self.inputs.new("mn_PolygonSocket", "Polygon")
		self.inputs.new("mn_MatrixSocket", "Matrix")
		self.outputs.new("mn_PolygonSocket", "Polygon")
		allowCompiling()
		
	def getInputSocketNames(self):
		return {"Polygon" : "polygon",
				"Matrix" : "matrix"}
	def getOutputSocketNames(self):
		return {"Polygon" : "polygon"}
		
	def execute(self, polygon, matrix):
		offsetMatrix = Matrix.Translation(polygon.center)
		transfromMatrix = offsetMatrix * matrix * offsetMatrix.inverted()
		
		for vertex in polygon.vertices:
			vertex.location = transfromMatrix * vertex.location
		
		return polygon
		
		

