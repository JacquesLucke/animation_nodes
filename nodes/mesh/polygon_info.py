import bpy
from bpy.props import *
from ... events import executionCodeChanged
from ... base_types.node import AnimationNode

class PolygonInfoNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_PolygonInfoNode"
    bl_label = "Polygon Info"

    copyVertices = BoolProperty(name = "Copy Vertices", default = False,
        description = "If unchecked the polygon is changed when the output vectors are changed",
        update = executionCodeChanged)

    def create(self):
        self.newInput("Polygon", "Polygon", "polygon")
        self.newOutput("Vector List", "Vertex Locations", "vertexLocations")
        self.newOutput("Vector", "Center", "center")
        self.newOutput("Vector", "Normal", "normal")
        self.newOutput("Float", "Area", "area")
        self.newOutput("Integer", "Material Index", "materialIndex")

    def getExecutionCode(self):
        isLinked = self.getLinkedOutputsDict()

        if self.copyVertices:
            if isLinked["vertexLocations"]: yield "vertexLocations = [v.copy() for v in polygon.vertexLocations]"
            if isLinked["center"]: yield "center = polygon.center.copy()"
            if isLinked["normal"]: yield "normal = polygon.normal.copy()"
        else:
            if isLinked["vertexLocations"]: yield "vertexLocations = polygon.vertexLocations"
            if isLinked["center"]: yield "center = polygon.center"
            if isLinked["normal"]: yield "normal = polygon.normal"

        if isLinked["area"]: yield "area = polygon.area"
        if isLinked["materialIndex"]: yield "materialIndex = polygon.materialIndex"
