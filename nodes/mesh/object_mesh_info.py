import bpy, time
from ... base_types.node import AnimationNode
from ... data_structures.mesh import MeshData, Vertex, Polygon
from ... cache import getLongTimeCache, setLongTimeCache, cacheFunctionResult
from ... events import propertyChanged

cacheIdentifier = "Object Mesh Data"

class ObjectMeshInfo(bpy.types.Node, AnimationNode):
    bl_idname = "mn_ObjectMeshInfo"
    bl_label = "Object Mesh Info"
    outputUseParameterName = "useOutput"

    inputNames = { "Object" : "object" }

    outputNames = { "Polygons" : "polygons",
                    "Vertices" : "vertices",
                    "Mesh Data" : "meshData" }

    usePerObjectCache = bpy.props.BoolProperty(
        name = "Use Cache",
        description = "Warning: Modifications to the data will overwrite the cache.",
        default = False)

    applyModifiers = bpy.props.BoolProperty(
        name = "Apply Modifiers",
        description = "Output the mesh with applied modifiers.",
        default = False, update = propertyChanged)

    def create(self):
        self.inputs.new("mn_ObjectSocket", "Object").showName = False
        self.outputs.new("mn_PolygonListSocket", "Polygons")
        self.outputs.new("mn_VertexListSocket", "Vertices")
        self.outputs.new("mn_MeshDataSocket", "Mesh Data")

    def draw_buttons(self, context, layout):
        layout.prop(self, "applyModifiers")

    def draw_buttons_ext(self, context, layout):
        layout.prop(self, "usePerObjectCache")

    def execute(self, object, useOutput):
        if getattr(object, "type", None) != "MESH":
            return [], [], MeshData()

        cache = self.getInitializedCache()

        polygons = []
        vertices = []
        meshData = MeshData()
        if self.applyModifiers:
            mesh = object.to_mesh(scene = bpy.context.scene, apply_modifiers = True, settings = "PREVIEW")
        else:
            mesh = object.data

        if useOutput["Polygons"]:
            polygons = cacheFunctionResult(cache, object.name + "POLYGONS", getPolygonsFromMesh, [mesh], self.usePerObjectCache)
        if useOutput["Vertices"]:
            vertices = cacheFunctionResult(cache, object.name + "VERTICES", getVerticesFromMesh, [mesh], self.usePerObjectCache)
        if useOutput["Mesh Data"]:
            meshData = cacheFunctionResult(cache, object.name + "MESH_DATA", getMeshDataFromMesh, [mesh], self.usePerObjectCache)

        if self.applyModifiers:
            bpy.data.meshes.remove(mesh)

        return polygons, vertices, meshData

    def getInitializedCache(self):
        cache = getLongTimeCache(cacheIdentifier)
        if cache is None:
            cache = {}
            setLongTimeCache(cacheIdentifier, cache)
        return cache


def getPolygonsFromMesh(mesh):
    polygons = []
    for polygon in mesh.polygons:
        vertices = []
        for vertexIndex in polygon.vertices:
            vertices.append(Vertex.fromMeshVertex(mesh.vertices[vertexIndex]))
        polygons.append(Polygon(vertices, polygon.area, polygon.center.copy(), polygon.normal.copy(), polygon.material_index))
    return polygons


def getVerticesFromMesh(mesh):
    vertices = []
    for vertex in mesh.vertices:
        vertices.append(Vertex.fromMeshVertex(vertex))
    return vertices


def getMeshDataFromMesh(mesh):
    vertices = getVertexLocationsFromMesh(mesh)
    edges = getEdgesIndicesFromMesh(mesh)
    polygons = getPolygonsIndicesFromMesh(mesh)
    return MeshData(vertices, edges, polygons)

def getVertexLocationsFromMesh(mesh):
    return [vertex.co.copy() for vertex in mesh.vertices]

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
