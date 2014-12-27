import bpy, bmesh
from mathutils import Vector

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
		return Vertex(v.co, v.normal, [groupWeight.weight for groupWeight in v.groups])
		
def getPolygonsFromMesh(mesh):
	polygons = []
	for polygon in mesh.polygons:
		vertices = []
		for vertex_index in polygon.vertices:
			vertices.append(Vertex.fromMeshVertex(mesh.vertices[vertex_index]))
		polygons.append(Polygon(vertices, polygon.area, polygon.center, polygon.normal, polygon.material_index))
	return polygons
	
def replaceMeshWithPolygons(mesh, polygons):
	bm = getBmeshFromMeshPydata(*getMeshPydataFromPolygons(polygons))
	bm.to_mesh(mesh)
	bm.free()
	
def getBmeshFromMeshPydata(vertexData, edgeData, faceData):
	bm = bmesh.new()
	for co in vertexData:
		bm.verts.new(co)
	bm.verts.ensure_lookup_table()
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