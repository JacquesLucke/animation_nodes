import bpy
from ... base_types import AnimationNode
from ... data_structures import LongList, DoubleList

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
        self.newOutput("Float List", "Bevel Vertex Weights", "bevelVertexWeights")
        self.newOutput("Float List", "Bevel Edge Weights", "bevelEdgeWeights")
        self.newOutput("Float List", "Edge Creases", "edgeCreases")
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
            yield "materialIndices = self.getBuiltInAttributes('Material Indices', mesh)"
        if "bevelVertexWeights" in required:
            yield "bevelVertexWeights = self.getBuiltInAttributes('Bevel Vertex Weights', mesh)"
        if "bevelEdgeWeights" in required:
            yield "bevelEdgeWeights = self.getBuiltInAttributes('Bevel Edge Weights', mesh)"
        if "edgeCreases" in required:
            yield "edgeCreases = self.getBuiltInAttributes('Edge Creases', mesh)"
        if "uvMapNames" in required:
            yield "uvMapNames = mesh.getAllUVMapAttributeNames()"
        if "vertexColorLayerNames" in required:
            yield "vertexColorLayerNames = mesh.getAllVertexColorAttributeNames()"
        if "customAttributeNames" in required:
            yield "customAttributeNames = mesh.getAllCustomAttributeNames()"

    def getBuiltInAttributes(self, name, mesh):
        builtInAttribute = mesh.getBuiltInAttribute(name)
        if builtInAttribute is None:
            if name == "Material Indices":
                data = LongList(length = len(mesh.polygons))
            elif name == "Bevel Vertex Weights":
                data = DoubleList(length = len(mesh.vertices))
            else:
                data = DoubleList(length = len(mesh.edges))
            
            data.fill(0)
            return data
        else:
            return builtInAttribute.data
