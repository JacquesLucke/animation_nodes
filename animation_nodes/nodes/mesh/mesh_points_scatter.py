import bpy
import random
from bpy.props import *
from ... events import propertyChanged
from ... base_types import AnimationNode
from . points_scatter import randomPointsScatter
from ... data_structures import Vector3DList, VirtualDoubleList

class MeshPointsScatterNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_MeshPointsScatterNode"
    bl_label = "Mesh Points Scatter"

    methodType: BoolProperty(name = "Use Advanced Method for Mesh sampling", default = False,
                             update = propertyChanged)

    nodeSeed: IntProperty(update = propertyChanged)

    def setup(self):
        self.randomizeNodeSeed()

    def create(self):
        self.newInput("Mesh", "Mesh", "mesh", dataIsModified = True)
        self.newInput("Integer", "Seed", "seed")
        self.newInput("Integer", "Amount", "amount", value = 10, minValue = 0)
        self.newInput("Float List", "Weights", "weights", hide = True)
        self.newInput("Boolean", "Use For Density", "useWeightForDensity", value = False, hide = True)

        self.newOutput("Vector List", "Points", "points")

    def draw(self, layout):
        row = layout.row(align = True)
        row.prop(self, "nodeSeed", text = "Node Seed")

    def drawAdvanced(self, layout):
        layout.prop(self, "methodType", text = "Use Advanced Method for Mesh sampling")

    def execute(self, mesh, seed, amount, weights, useWeightForDensity):
        vertices = mesh.vertices
        polygons = mesh.polygons

        if len(vertices) == 0 or len(polygons) == 0 or amount == 0:
            return Vector3DList()

        if polygons.polyLengths.getMaxValue() > 3:
            if self.methodType: polygons = mesh.getTrianglePolygons(method = "EAR")
            else: polygons = mesh.getTrianglePolygons(method = "FAN")

        weights = VirtualDoubleList.create(weights, 1)
        seed  = (seed * 674523 + self.nodeSeed * 3465284) % 0x7fffffff
        return randomPointsScatter(vertices, polygons, weights, useWeightForDensity, seed, amount)

    def duplicate(self, sourceNode):
        self.randomizeNodeSeed()

    def randomizeNodeSeed(self):
        self.nodeSeed = int(random.random() * 100)
