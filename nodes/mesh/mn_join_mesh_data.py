import bpy, bmesh
from bpy.types import Node
from animation_nodes.mn_node_base import AnimationNode
from animation_nodes.mn_execution import nodePropertyChanged, nodeTreeChanged, allowCompiling, forbidCompiling
from animation_nodes.utils.mn_mesh_utils import *
import bmesh

join_type_items = [
	("POLYGONS_ONLY", "Polygons only", ""),
	("NORMAL", "Vertices and Indices", "") ]

class mn_JoinMeshData(Node, AnimationNode):
	bl_idname = "mn_JoinMeshData"
	bl_label = "Join Mesh Data"
	
	def selectedTypeChanged(self, context):
		self.changeHideStatusOfSockets()
	
	join_type = bpy.props.EnumProperty(items = join_type_items, name = "Creation Type", update = selectedTypeChanged)
	
	def init(self, context):
		forbidCompiling()
		self.inputs.new("mn_PolygonListSocket", "A Polygons")
		self.inputs.new("mn_VertexListSocket", "A Vertices")
		self.inputs.new("mn_IntegerList2DSocket", "A Edges Indices")
		self.inputs.new("mn_IntegerList2DSocket", "A Polygons Indices")
		self.inputs.new("mn_PolygonListSocket", "B Polygons")
		self.inputs.new("mn_VertexListSocket", "B Vertices")
		self.inputs.new("mn_IntegerList2DSocket", "B Edges Indices")
		self.inputs.new("mn_IntegerList2DSocket", "B Polygons Indices")

		self.outputs.new("mn_PolygonListSocket", "Polygons")
		self.outputs.new("mn_VertexListSocket", "Vertices")
		self.outputs.new("mn_IntegerList2DSocket", "Edges Indices")
		self.outputs.new("mn_IntegerList2DSocket", "Polygons Indices")
		
		self.changeHideStatusOfSockets()
		allowCompiling()
		
	def draw_buttons(self, context, layout):
		layout.prop(self, "join_type")
		
	def getInputSocketNames(self):
		return {"A Polygons" : "polygonsA",
				"A Vertices" : "verticesA",
				"A Edges Indices" : "edgesIndicesA",
				"A Polygons Indices" : "polygonsIndicesA",
				"B Polygons" : "polygonsB",
				"B Vertices" : "verticesB",
				"B Edges Indices" : "edgesIndicesB",
				"B Polygons Indices" : "polygonsIndicesB"}
	def getOutputSocketNames(self):
		return {"Polygons" : "polygons",
				"Vertices" : "vertices",
				"Edges Indices" : "edgesIndices",
				"Polygons Indices" : "polygonsIndices"}
		
	def execute(self, polygonsA, verticesA, edgesIndicesA, polygonsIndicesA,
				polygonsB, verticesB, edgesIndicesB, polygonsIndicesB):
		if self.join_type == "POLYGONS_ONLY":
			return polygonsA + polygonsB, [], [], []
		if self.join_type == "NORMAL":
			vertices = verticesA + verticesB
			
			offset = len(verticesA)
			edgesIndices = edgesIndicesA
			for edge in edgesIndicesB:
				edgesIndices.append((edge[0] + offset, edge[1] + offset))
			polygonsIndices = polygonsIndicesA
			for poly in polygonsIndicesB:
				polygonsIndices.append(tuple([index + offset for index in poly]))
			return [], vertices, edgesIndices, polygonsIndices
		
	def changeHideStatusOfSockets(self):
		self.inputs["A Polygons"].hide = True
		self.inputs["A Vertices"].hide = True
		self.inputs["A Edges Indices"].hide = True
		self.inputs["A Polygons Indices"].hide = True
		
		self.inputs["B Polygons"].hide = True
		self.inputs["B Vertices"].hide = True
		self.inputs["B Edges Indices"].hide = True
		self.inputs["B Polygons Indices"].hide = True
		
		self.outputs["Polygons"].hide = True
		self.outputs["Vertices"].hide = True
		self.outputs["Edges Indices"].hide = True
		self.outputs["Polygons Indices"].hide = True
		
		if self.join_type == "POLYGONS_ONLY":
			self.inputs["A Polygons"].hide = False
			self.inputs["B Polygons"].hide = False			
			self.outputs["Polygons"].hide = False
		if self.join_type == "NORMAL":
			self.inputs["A Vertices"].hide = False
			self.inputs["A Edges Indices"].hide = False
			self.inputs["A Polygons Indices"].hide = False
			
			self.inputs["B Vertices"].hide = False
			self.inputs["B Edges Indices"].hide = False
			self.inputs["B Polygons Indices"].hide = False
			
			self.outputs["Vertices"].hide = False
			self.outputs["Edges Indices"].hide = False
			self.outputs["Polygons Indices"].hide = False