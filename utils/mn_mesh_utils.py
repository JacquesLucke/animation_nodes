import bpy, bmesh
from mathutils import Vector
from animation_nodes.mn_utils import *

class Polygon:
	def __init__(self, 
				vertex_positions = [], 
				area = 0, 
				center = Vector((0, 0, 0)), 
				normal = Vector((0, 0, 1)),
				materialIndex = 0):
		self.vertices = vertex_positions
		self.area = area
		self.center = center
		self.normal = normal
		self.materialIndex = materialIndex
		
	def __repr__(self):
		return "Polygon - Center: " + str(self.center) + " Vertices: " + str(len(self.vertices))
		
class Vertex:
	def __init__(self,
				location = Vector((0, 0, 0)),
				normal = Vector((0, 0, 1)),
				groupWeights = []):
		self.location = location
		self.normal = normal
		self.groupWeights = groupWeights
	
	@classmethod
	def fromMeshVertex(cls, v):
		return Vertex(v.co.copy(), v.normal.copy(), [groupWeight.weight for groupWeight in v.groups])
		
	def __repr__(self):
		return "Vertex - " + str(self.location)
		
def getPolygonsFromMesh(mesh):
	polygons = []
	for polygon in mesh.polygons:
		vertices = []
		for vertex_index in polygon.vertices:
			vertices.append(Vertex.fromMeshVertex(mesh.vertices[vertex_index]))
		polygons.append(Polygon(vertices, polygon.area, polygon.center.copy(), polygon.normal.copy(), polygon.material_index))
	return polygons
	
def getVerticesFromMesh(mesh):
	vertices = []
	for vertex in mesh.vertices:
		vertices.append(Vertex.fromMeshVertex(vertex))
	return vertices
	
def getEdgesIndicesFromMesh(mesh):
	edgesIndices = []
	for edge in mesh.edges:
		edgesIndices.append((edge.vertices[0], edge.vertices[1]))
	return edgesIndices
	
def getPolygonsIndicesFromMesh(mesh):
	polygonsIndices = []
	for polygon in mesh.polygons:
		polygonsIndices.append(polygon.vertices[:])
	return polygonsIndices
	
def getBMeshFromPolygons(polygons):
	return getBMeshFromMeshPydata(*getMeshPydataFromPolygons(polygons))
	
def getBMeshFromVerticesAndIndices(vertices, edgesIndices, polygonsIndices):
	return getBMeshFromMeshPydata(getLocationsFromVertices(vertices), edgesIndices, polygonsIndices)
	
def getBMeshFromMeshPydata(vertexData, edgeData, faceData):
	bm = bmesh.new()
	for co in vertexData:
		bm.verts.new(co)
		
	# for Blender Version >= 2.73
	try: bm.verts.ensure_lookup_table()
	except: pass
	
	for edgeIndices in edgeData:
		bm.edges.new((bm.verts[edgeIndices[0]], bm.verts[edgeIndices[1]]))
	for faceIndices in faceData:
		bm.faces.new(tuple(bm.verts[index] for index in faceIndices))
	return bm
	
def getMeshPydataFromPolygons(polygons):
	vertexData = []
	faceData = []
	
	index = 0
	for polygon in polygons:
		vertexData.extend([v.location for v in polygon.vertices])
		vertexAmount = len(polygon.vertices)
		faceData.append(tuple(range(index, index + vertexAmount)))
		index += vertexAmount
		
	return vertexData, [], faceData
	
def getLocationsFromVertices(vertices):
	vertexData = [vertex.location for vertex in vertices]
	return vertexData