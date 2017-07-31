import bpy
from ... base_types import AnimationNode

class IntersectLinePlaneNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_IntersectLinePlaneNode"
    bl_label = "Intersect Line Plane"
    bl_width_default = 160

    def create(self):
        self.newInput("Vector", "Line Start", "lineStart")
        self.newInput("Vector", "Line End", "lineEnd", value = (0, 0, 1))

        self.newInput("Vector", "Plane Point", "planePoint")
        self.newInput("Vector", "Plane Normal", "planeNormal", value = (0, 0, 1))

        self.newOutput("Vector", "Intersection", "intersection")
        self.newOutput("Boolean", "Is Valid", "isValid")

    def getExecutionCode(self, required):
        if len(required) == 0:
            return

        yield "if planeNormal.length_squared == 0: planeNormal = Vector((0, 0, 1))"
        yield "_intersection = mathutils.geometry.intersect_line_plane(lineStart, lineEnd, planePoint, planeNormal, False)"

        yield "if _intersection is None:"
        if "intersection" in required: yield "    intersection = Vector((0, 0, 0))"
        if "isValid" in required:      yield "    isValid = False"
        yield "else:"
        if "intersection" in required: yield "    intersection = _intersection"
        if "isValid" in required:      yield "    isValid = True"

    def getUsedModules(self):
        return ["mathutils"]
