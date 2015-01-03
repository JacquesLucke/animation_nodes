import bpy, bmesh
from mathutils import Vector
from animation_nodes.mn_utils import *

class MeshData:
	def __init__(self,
				vertices = [],
				edges = [],
				polygons = []):
		self.vertices = vertices
		self.edges = edges
		self.polygons = polygons
		
	def copy(self):
		return MeshData(self.getVerticesCopy(), self.getEdgesCopy(), self.getPolygonsCopy())

	def getVerticesCopy(self):
		return [vertex.copy() for vertex in self.vertices]
	def getEdgesCopy(self):
		return copy2dList(self.edges)
	def getPolygonsCopy(self):
		return copy2dList(self.polygons)
		

class Polygon:
	def __init__(self, 
				vertexPositions = [], 
				area = 0, 
				center = Vector((0, 0, 0)), 
				normal = Vector((0, 0, 1)),
				materialIndex = 0):
		self.vertices = vertexPositions
		self.area = area
		self.center = center
		self.normal = normal
		self.materialIndex = materialIndex
		
	def __repr__(self):
		return "Polygon - Center: " + str(self.center) + " Vertices: " + str(len(self.vertices))
		
	def copy(self):
		return Polygon([vector.copy() for vector in self.vertices], self.area, self.center.copy(), self.normal.copy(), self.materialIndex)
		
		
def copy2dList(list):
	return [element[:] for element in list]	
	
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
		
	def copy(self):
		return Vertex(self.location.copy(), self.normal.copy(), [weight for weight in self.groupWeights])
		