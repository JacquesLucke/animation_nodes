import bpy
from mathutils import Vector

class Face:
    def __init__(self, 
				vertex_positions = [], 
				area = 0, 
				center = Vector((0, 0, 0)), 
				normal = Vector((0, 0, 0)),
				material_index = 0):
        self.vertices = vertex_positions
        self.area = area
        self.center = center
        self.normal = normal
        self.material_index = material_index
		
def get_faces_from_mesh(mesh):
	faces = []
	for polygon in mesh.polygons:
		vertices = []
		for vertex_index in polygon.vertices:
			vertices.append(mesh.vertices[vertex_index].co)
		face = Face(vertices, polygon.area, polygon.center, polygon.normal, polygon.material_index)
		faces.append(face)
	return faces
	
def new_mesh_from_faces(faces, name = "mesh"):
	vertex_data = []
	face_data = []
	
	index = 0
	for face in faces:
		vertex_data.extend(face.vertices)
		vertex_amount = len(face.vertices)
		face_data.append(range(index, index + vertex_amount))
		index += vertex_amount
		
	mesh = bpy.data.meshes.new(name = name)
	mesh.from_pydata(vertex_data, [], face_data)
	return mesh