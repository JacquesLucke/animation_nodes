import bpy
from ... base_types.node import AnimationNode

class RotationToDirectionNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_RotationToDirectionNode"
    bl_label = "Rotation to Direction"

    def create(self):
        self.inputs.new("an_EulerSocket", "Rotation", "rotation")
        self.inputs.new("an_FloatSocket", "Length", "length").value = 1
        self.outputs.new("an_VectorSocket", "Direction", "direction")

    def getExecutionCode(self):
        yield "matrix = rotation.to_matrix(); matrix.resize_4x4()"
        yield "direction = matrix * mathutils.Vector((0, 0, length))"

    def getUsedModules(self):
        return ["mathutils"]
