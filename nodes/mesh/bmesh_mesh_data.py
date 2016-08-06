import bpy
from bpy.props import *
from ... data_structures import Vector3DList
from ... base_types.node import AnimationNode

class BMeshMeshDataNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_BMeshMeshDataNode"
    bl_label = "BMesh Mesh Data"

    def create(self):
        self.newInput("BMesh", "BMesh", "bm")

        self.newOutput("Vector List", "Vertex Locations", "vertexLocations")
        self.newOutput("Edge Indices List", "Edge Indices", "edgeIndices")
        self.newOutput("Polygon Indices List", "Polygon Indices", "polygonIndices")

    def getExecutionCode(self):
        isLinked = self.getLinkedOutputsDict()
        if not any(isLinked.values()): return

        yield "if bm:"
        if isLinked["vertexLocations"]:
            yield "    vertexLocations = self.getVertexLocations(bm)"
        if isLinked["edgeIndices"]:
            yield "    edgeIndices = self.getEdgeIndices(bm)"
        if isLinked["polygonIndices"]:
            yield "    polygonIndices = self.getPolygonIndices(bm)"

        yield "else: vertexLocations, edgeIndices, polygonIndices = [], [], []"

    def getVertexLocations(self, bMesh):
        return Vector3DList.fromValues(v.co for v in bMesh.verts)

    def getEdgeIndices(self, bMesh):
        return [tuple(v.index for v in edge.verts) for edge in bMesh.edges]

    def getPolygonIndices(self, bMesh):
        return [tuple(v.index for v in face.verts) for face in bMesh.faces]
