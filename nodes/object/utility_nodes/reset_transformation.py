import bpy
from .... base_types.node import AnimationNode

class ResetObjectTransformsNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_ResetObjectTransformsNode"
    bl_label = "Reset Object Transforms"

    def create(self):
        self.inputs.new("an_ObjectSocket", "Object", "object").defaultDrawType = "PROPERTY_ONLY"
        self.outputs.new("an_ObjectSocket", "Object", "object")

    def getExecutionCode(self):
        return "if object: object.matrix_world = mathutils.Matrix.Identity(4)"

    def getUsedModules(self):
        return ["mathutils"]
