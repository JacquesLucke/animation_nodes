import bpy
from mathutils import Vector
from ... base_types.node import AnimationNode

class DistanceVectorToLineNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_DistanceVectorToLineNode"
    bl_label = "Distance Vector to Line"
    bl_width_default = 160

    def create(self):
        self.inputs.new("an_VectorSocket", "Vector", "vector")
        self.inputs.new("an_VectorSocket", "Point on Line", "linePoint")
        self.inputs.new("an_VectorSocket", "Line Direction", "lineDirection").value = (0, 0, 1)
        self.outputs.new("an_FloatSocket", "Distance", "distance")

    def execute(self, vector, linePoint, lineDirection):
        directionLength = lineDirection.length
        if directionLength == 0:
            return 0

        lineDirection = lineDirection.normalized()
        parameter = (lineDirection.dot(vector - linePoint)) / directionLength
        return (linePoint + lineDirection * parameter - vector).length
