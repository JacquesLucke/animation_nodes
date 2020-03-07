import bpy
import math
import random
from bpy.props import *
from ... events import propertyChanged
from ... base_types import AnimationNode
from . c_utils import trianglePolygonsArea, triangulatePolygons
from ... algorithms.random import uniformRandomDoubleWithTwoSeeds
from ... data_structures import LongList, FloatList, Vector3DList, VirtualDoubleList

class MeshPointsScatterNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_MeshPointsScatterNode"
    bl_label = "Mesh Points Scatter"
    errorHandlingType = "EXCEPTION"

    nodeSeed: IntProperty(update = propertyChanged)

    triangulate: BoolProperty(name = "Triangulate Mesh", default = False,
        update = AnimationNode.refresh)

    def setup(self):
        self.randomizeNodeSeed()

    def create(self):
        self.newInput("Mesh", "Mesh", "mesh", dataIsModified = True)
        self.newInput("Integer", "Seed", "seed")
        self.newInput("Integer", "Amount", "amount", value = 10, minValue = 0)
        self.newInput("Float List", "Weights", "weights")

        self.newOutput("Vector List", "Points", "points")

    def draw(self, layout):
        row = layout.row(align = True)
        row.prop(self, "nodeSeed", text = "Node Seed")
        row = layout.row(align = True)
        row.prop(self, "triangulate", text = "Triangulate Mesh")

    def execute(self, mesh, seed, amount, weights):
        vertices = mesh.vertices
        polygons = mesh.polygons

        if len(vertices) == 0 or len(polygons) == 0 or amount == 0:
            return Vector3DList()

        if self.triangulate: polygons = triangulatePolygons(polygons)
        if polygons.polyLengths.getMaxValue() > 3:
            self.raiseErrorMessage("Mesh should have triangle polygons.")

        return self.randomPointsScatter(vertices, polygons, seed, amount, weights)

    # Mesh Sampling basis on Barycentric Coordinate System: http://www.joesfer.com/?p=84
    def randomPointsScatter(self, vertices, polygons, seed, amount, weights):
        areas = trianglePolygonsArea(vertices, polygons)
        areaMin = areas.getMinValue()
        if areaMin == 0: self.raiseErrorMessage("Remove doubles.")

        if len(weights) != 0:
            usePolyWeight = True
            polyAmount = len(polygons)
            polyWeights = FloatList(length = polyAmount)
            weights = VirtualDoubleList.create(weights, 1).materialize(polyAmount)
            for i, polygon in enumerate(polygons):
                polyWeights[i] = (weights[polygon[0]] + weights[polygon[1]] + weights[polygon[2]]) / 3
        else:
            usePolyWeight = False

        probabilities = LongList()
        if usePolyWeight:
            for i, area in enumerate(areas):
                polyRange = int(area * polyWeights[i] / areaMin)
                for j in range(polyRange):
                    probabilities.append(i)
        else:
            for i, area in enumerate(areas):
                polyRange = int(area / areaMin)
                for j in range(polyRange):
                    probabilities.append(i)

        lenProb = len(probabilities)
        if lenProb == 0: return Vector3DList()
        points = Vector3DList(length = amount)
        for i in range(amount):
            randIndex = probabilities[int(uniformRandomDoubleWithTwoSeeds(seed + i, self.nodeSeed, 0, lenProb))]
            polygon = polygons[randIndex]
            points[i] = self.randomPolyPoint(i, vertices, polygon, seed)
        return points

    def randomPolyPoint(self, index, vertices, polygon, seed):
        v1 = vertices[polygon[0]]
        v2 = vertices[polygon[1]]
        v3 = vertices[polygon[2]]
        p = self.randomPairGenerator(index, seed)
        return p[0] * v1 + p[1] * v2 + p[2] * v3

    def randomPairGenerator(self, index, seed):
        p1 = uniformRandomDoubleWithTwoSeeds(seed + index, self.nodeSeed + index, 0, 1)
        p2 = uniformRandomDoubleWithTwoSeeds(seed + index + 100, self.nodeSeed + index + 100, 0, 1)
        u = 1 - math.sqrt(p1)
        v = p2 * math.sqrt(p1)
        w = 1 - u - v
        return u, v, w

    def duplicate(self, sourceNode):
        self.randomizeNodeSeed()

    def randomizeNodeSeed(self):
        self.nodeSeed = int(random.random() * 100)
