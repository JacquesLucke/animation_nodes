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
        self.newInput("an_PolygonSocket", "Polygon", "polygon")
        self.newOutput("an_VectorListSocket", "Vertex Locations", "vertexLocations")
        self.newOutput("an_VectorSocket", "Center", "center")
        self.newOutput("an_VectorSocket", "Normal", "normal")
        self.newOutput("an_FloatSocket", "Area", "area")
        self.newOutput("an_IntegerSocket", "Material Index", "materialIndex")

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
