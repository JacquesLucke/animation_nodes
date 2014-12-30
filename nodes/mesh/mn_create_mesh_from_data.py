import bpy, bmesh
from bpy.types import Node
from animation_nodes.mn_node_base import AnimationNode
from animation_nodes.mn_execution import nodePropertyChanged, nodeTreeChanged, allowCompiling, forbidCompiling
from animation_nodes.utils.mn_mesh_utils import *
import bmesh

creation_type_items = [
	("POLYGONS_ONLY", "Polygons only", ""),
	("MESH_DATA", "Mesh Data", "") ]

class mn_CreateMeshFromData(Node, AnimationNode):
	bl_idname = "mn_CreateMeshFromData"
	bl_label = "Create Mesh"
	
	def selectedTypeChanged(self, context):
		self.changeHideStatusOfSockets()
	
	creation_type = bpy.props.EnumProperty(items = creation_type_items, name = "Creation Type", update = selectedTypeChanged)
	
	def init(self, context):
		forbidCompiling()
		self.inputs.new("mn_PolygonListSocket", "Polygons")
		self.inputs.new("mn_MeshDataSocket", "Mesh Data")
		self.changeHideStatusOfSockets()
		self.outputs.new("mn_MeshSocket", "Mesh")
		allowCompiling()
		
	def draw_buttons(self, context, layout):
		layout.prop(self, "creation_type", text = "Type")
		
	def getInputSocketNames(self):
		return {"Polygons" : "polygons",
				"Mesh Data" : "meshData"}
	def getOutputSocketNames(self):
		return {"Mesh" : "mesh"}
		
	def execute(self, polygons, meshData):
		if self.creation_type == "POLYGONS_ONLY":
			return getBMeshFromPolygons(polygons)
		if self.creation_type == "MESH_DATA":
			return getBMeshFromMeshData(meshData)
		return bmesh.new()
		
	def changeHideStatusOfSockets(self):
		self.inputs["Polygons"].hide = True
		self.inputs["Mesh Data"].hide = True
		
		if self.creation_type == "POLYGONS_ONLY":
			self.inputs["Polygons"].hide = False
		if self.creation_type == "MESH_DATA":
			self.inputs["Mesh Data"].hide = False
			
def getBMeshFromPolygons(polygons):
	return getBMeshFromMeshData(getMeshDataFromPolygons(polygons))	
	
def getMeshDataFromPolygons(polygons):
	vertices = []
	polygonsIndices = []
	
	index = 0
	for polygon in polygons:
		vertices.extend([v.location for v in polygon.vertices])
		vertexAmount = len(polygon.vertices)
		polygonsIndices.append(tuple(range(index, index + vertexAmount)))
		index += vertexAmount
		
	return MeshData(vertices, [], polygonsIndices)
	
def getBMeshFromMeshData(meshData):
	bm = bmesh.new()
	for co in meshData.vertices:
		bm.verts.new(co)
		
	# for Blender Version >= 2.73
	try: bm.verts.ensure_lookup_table()
	except: pass
	
	for edgeIndices in meshData.edges:
		bm.edges.new((bm.verts[edgeIndices[0]], bm.verts[edgeIndices[1]]))
	for polygonIndices in meshData.polygons:
		bm.faces.new(tuple(bm.verts[index] for index in polygonIndices))
	return bm