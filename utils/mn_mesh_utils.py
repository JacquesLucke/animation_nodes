import bpy, bmesh
from mathutils import Vector

class Polygon:
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
		
def get_polygons_from_mesh(mesh):
	polygons = []
	for polygon in mesh.polygons:
		vertices = []
		for vertex_index in polygon.vertices:
			vertices.append(mesh.vertices[vertex_index].co)
		polygons.append(Polygon(vertices, polygon.area, polygon.center, polygon.normal, polygon.material_index))
	return polygons
	
def new_mesh_from_polygons(polygons, name = "mesh"):
	mesh = bpy.data.meshes.new(name = name)
	mesh.from_pydata(*get_mesh_pydata_from_polygons(polygons))
	return mesh
	
def replace_mesh_by_polygons(mesh, polygons):
	bm = get_bmesh_from_mesh_pydata(*get_mesh_pydata_from_polygons(polygons))
	bm.to_mesh(mesh)
	bm.free()
	
def get_bmesh_from_mesh_pydata(vertex_data, edge_data, face_data):
	bm = bmesh.new()
	for co in vertex_data:
		bm.verts.new(co)
	bm.verts.ensure_lookup_table()
	for edge_indices in edge_data:
		bm.edges.new((bm.verts[edge_indices[0]], bm.verts[edge_indices[1]]))
	for face_indices in face_data:
		bm.faces.new(tuple(bm.verts[index] for index in face_indices))
	return bm
	
def get_mesh_pydata_from_polygons(polygons):
	vertex_data = []
	face_data = []
	
	index = 0
	for polygon in polygons:
		vertex_data.extend(polygon.vertices)
		vertex_amount = len(polygon.vertices)
		face_data.append(tuple(range(index, index + vertex_amount)))
		index += vertex_amount
		
	return vertex_data, [], face_data