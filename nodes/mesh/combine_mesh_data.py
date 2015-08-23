import bpy
from bpy.props import *
from ... events import propertyChanged
from ... base_types.node import AnimationNode
from ... data_structures.mesh import MeshData

sourceTypeItems = [
    ("MESH_DATA", "Vertices and Indices", ""),
    ("POLYGONS", "Polygons", "") ]

class CombineMeshData(bpy.types.Node, AnimationNode):
    bl_idname = "an_CombineMeshData"
    bl_label = "Combine Mesh Data"

    def sourceTypeChanged(self, context):
        self.updateHideStatus()
        propertyChanged(self, context)

    sourceType = EnumProperty(items = sourceTypeItems, default = "MESH_DATA", name = "Source Type", update = sourceTypeChanged)

    def create(self):
        self.inputs.new("an_VectorListSocket", "Vertex Locations", "vertexLocations").dataIsModified = True
        self.inputs.new("an_EdgeIndicesListSocket", "Edges Indices", "edgesIndices").dataIsModified = True
        self.inputs.new("an_PolygonIndicesListSocket", "Polygons Indices", "polygonsIndices").dataIsModified = True
        self.inputs.new("an_PolygonListSocket", "Polygons", "polygons").dataIsModified = True
        self.updateHideStatus()
        self.outputs.new("an_MeshDataSocket", "Mesh Data", "meshData")

    def draw(self, layout):
        layout.prop(self, "sourceType")

    def execute(self, vertexLocations, edgesIndices, polygonsIndices, polygons):
        if self.sourceType == "MESH_DATA":
            meshData = MeshData(vertexLocations, edgesIndices, polygonsIndices)
        elif self.sourceType == "POLYGONS":
            meshData = getMeshDataFromPolygons(polygons)

        return meshData

    def updateHideStatus(self):
        self.inputs["Vertex Locations"].hide = True
        self.inputs["Edges Indices"].hide = True
        self.inputs["Polygons Indices"].hide = True
        self.inputs["Polygons"].hide = True

        if self.sourceType == "MESH_DATA":
            self.inputs["Vertex Locations"].hide = False
            self.inputs["Edges Indices"].hide = False
            self.inputs["Polygons Indices"].hide = False
        elif self.sourceType == "POLYGONS":
            self.inputs["Polygons"].hide = False


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
