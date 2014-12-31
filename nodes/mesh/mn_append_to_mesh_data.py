import bpy, bmesh
from bpy.types import Node
from animation_nodes.mn_node_base import AnimationNode
from animation_nodes.mn_execution import nodePropertyChanged, nodeTreeChanged, allowCompiling, forbidCompiling
from animation_nodes.utils.mn_mesh_utils import *
import bmesh

class mn_AppendToMeshData(Node, AnimationNode):
	bl_idname = "mn_AppendToMeshData"
	bl_label = "Append Mesh Data"
	
	def init(self, context):
		forbidCompiling()
		self.inputs.new("mn_MeshDataSocket", "Mesh Data")
		self.inputs.new("mn_MeshDataSocket", "Other")
		self.outputs.new("mn_MeshDataSocket", "Joined Mesh Data")
		allowCompiling()
		
	def getInputSocketNames(self):
		return {"Mesh Data" : "meshDataA",
				"Other" : "meshDataB"}
	def getOutputSocketNames(self):
		return {"Joined Mesh Data" : "meshData"}
		
	def execute(self, meshDataA, meshDataB):
		newVertices = meshDataB.vertices
		newEdges = meshDataB.edges
		newPolygons = meshDataB.polygons
		
		if meshDataA.vertices == newVertices:
			newVertices = meshDataB.getVerticesCopy()
		if meshDataA.edges == newEdges:
			newEdges = meshDataB.getEdgesCopy()
		if meshDataA.polygons == newPolygons:
			newPolygons = meshDataB.getPolygonsCopy()
	
		meshData = meshDataA
		offset = len(meshDataA.vertices)
		
		meshData.vertices += newVertices
		
		for edge in newEdges:
			meshData.edges.append((edge[0] + offset, edge[1] + offset))
			
		for poly in newPolygons:
			meshData.polygons.append(tuple([index + offset for index in poly]))
			
		return meshData