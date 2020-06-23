import bpy
import random
from bpy.props import *
from ... utils.math import cantorPair
from ... events import propertyChanged
from ... base_types import AnimationNode
from ... data_structures import Matrix4x4List, VirtualDoubleList
from ... data_structures.meshes.mesh_data import calculatePolygonNormals
from ... algorithms.mesh.points_scatter import randomPointsScatter, randomPointsScatterForEdges
from ... algorithms.mesh.triangulate_mesh import (
    triangulatePolygonsUsingFanSpanMethod,
    triangulatePolygonsUsingEarClipMethod
)

modeItems = [
    ("EDGES", "Edges", "Scatter points on edges", "NONE", 0),
    ("POLYGONS", "Polygons", "Scatter points on polygons", "NONE", 1)
]

class MeshPointsScatterNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_MeshPointsScatterNode"
    bl_label = "Mesh Points Scatter"

    mode: EnumProperty(name = "Mode", default = "POLYGONS",
        items = modeItems, update = AnimationNode.refresh)

    methodType: BoolProperty(name = "Use Advanced Method for Mesh sampling", default = False,
                             update = propertyChanged)

    nodeSeed: IntProperty(update = propertyChanged, min = 0)

    def setup(self):
        self.randomizeNodeSeed()

    def create(self):
        self.newInput("Mesh", "Mesh", "mesh")
        self.newInput("Integer", "Seed", "seed", minValue = 0)
        self.newInput("Integer", "Amount", "amount", value = 10, minValue = 0)
        self.newInput("Float List", "Weights", "weights", hide = True)

        self.newOutput("Matrix List", "Matrices", "matrices")
        self.newOutput("Vector List", "Vectors", "vectors")

    def draw(self, layout):
        row = layout.row(align = True)
        layout.prop(self, "mode", text = "")
        row.prop(self, "nodeSeed", text = "Node Seed")

    def drawAdvanced(self, layout):
        layout.prop(self, "methodType", text = "Use Advanced Method for Mesh sampling")

    def getExecutionCode(self, required):
        yield "matrices = self.execute_RandomPointsScatter(mesh, seed, amount, weights)"

        if "vectors" in required:
            yield "vectors = AN.nodes.matrix.c_utils.extractMatrixTranslations(matrices)"

    def execute_RandomPointsScatter(self, mesh, seed, amount, weights):
        vertices = mesh.vertices
        polygons = mesh.polygons
        edges = mesh.edges

        if len(vertices) == 0 or amount == 0:
            return Matrix4x4List()

        weights = VirtualDoubleList.create(weights, 1)
        seed = cantorPair(int(max(seed, 0)), self.nodeSeed)
        if self.mode == "POLYGONS":
            if len(polygons) == 0: return Matrix4x4List()
            if polygons.polyLengths.getMaxValue() > 3:
                if self.methodType:
                    polygons = triangulatePolygonsUsingEarClipMethod(vertices, polygons)
                else:
                    polygons = triangulatePolygonsUsingFanSpanMethod(polygons)
            polyNormals = calculatePolygonNormals(vertices, polygons)
            return randomPointsScatter(vertices, polygons, polyNormals, weights, seed, max(amount, 0))
        else:
            if len(edges) == 0: return Matrix4x4List()
            return randomPointsScatterForEdges(vertices, edges, weights, seed, max(amount, 0))

    def duplicate(self, sourceNode):
        self.randomizeNodeSeed()

    def randomizeNodeSeed(self):
        self.nodeSeed = int(random.random() * 100)
