import bpy
from bpy.props import *
from ... base_types.node import AnimationNode

class ProjectPointOnLineNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_ProjectPointOnLineNode"
    bl_label = "Project Point on Line"
    searchTags = ["Distance Point to Line", "Closest Point on Line"]

    def create(self):
        self.width = 160
        self.inputs.new("an_VectorSocket", "Point", "point")
        self.inputs.new("an_VectorSocket", "Line Start", "lineStart").value = (0, 0, 0)
        self.inputs.new("an_VectorSocket", "Line End", "lineEnd").value = (0, 0, 1)

        self.outputs.new("an_VectorSocket", "Projection", "projection")
        self.outputs.new("an_FloatSocket", "Projection Factor", "factor")
        self.outputs.new("an_FloatSocket", "Distance", "distance")

    def getExecutionCode(self):
        isLinked = self.getLinkedOutputsDict()
        if not any(isLinked.values()):
            return

        yield "if lineStart == lineEnd: projection, factor = lineStart, 0.0"
        yield "else: projection, factor = mathutils.geometry.intersect_point_line(point, lineStart, lineEnd)"
        
        if isLinked["distance"]:
            yield "distance = (projection - point).length"

    def getUsedModules(self):
        return ["mathutils"]
