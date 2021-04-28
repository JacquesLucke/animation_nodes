import bpy
from ... base_types import AnimationNode
from ... data_structures import LongList

class MeshInfoNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_MeshInfoNode"
    bl_label = "Mesh Info"

    def create(self):
        self.newInput("Mesh", "Mesh", "mesh", dataIsModified = True)
        self.newOutput("Vector List", "Vertex Locations", "vertices")
        self.newOutput("Edge Indices List", "Edge Indices", "edgeIndices")
        self.newOutput("Polygon Indices List", "Polygon Indices", "polygonIndices")
        self.newOutput("Vector List", "Vertex Normals", "vertexNormals")
        self.newOutput("Vector List", "Polygon Centers", "polygonCenters")
        self.newOutput("Vector List", "Polygon Normals", "polygonNormals")
        self.newOutput("Integer List", "Material Indices", "materialIndices")
        self.newOutput("Text List", "UV Map Names", "uvMapNames")
        self.newOutput("Text List", "Vertex Color Layers", "vertexColorLayerNames")
        self.newOutput("Text List", "Custom Attribute Names", "customAttributeNames")

    def getExecutionCode(self, required):
        if "vertices" in required:
            yield "vertices = mesh.vertices"
        if "edgeIndices" in required:
            yield "edgeIndices = mesh.edges"
        if "polygonIndices" in required:
            yield "polygonIndices = mesh.polygons"
        if "vertexNormals" in required:
            yield "vertexNormals = mesh.getVertexNormals()"
        if "polygonNormals" in required:
            yield "polygonNormals = mesh.getPolygonNormals()"
        if "polygonCenters" in required:
            yield "polygonCenters = mesh.getPolygonCenters()"
        if "materialIndices" in required:
            yield "materialIndices = self.getMaterialIndices(mesh)"
        if "uvMapNames" in required:
            yield "uvMapNames = mesh.getAllUVMapAttributeNames()"
        if "vertexColorLayerNames" in required:
            yield "vertexColorLayerNames = mesh.getAllVertexColorAttributeNames()"
        if "customAttributeNames" in required:
            yield "customAttributeNames = mesh.getAllCustomAttributeNames()"

    def getMaterialIndices(self, mesh):
        materialIndices = mesh.getBuiltInAttribute("Material Indices")
        if materialIndices is None:
            indices = LongList(length = len(mesh.polygons))
            indices.fill(0)
            return indices
        else:
            return materialIndices.data
