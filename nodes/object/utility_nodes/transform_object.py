import bpy
from .... base_types.node import AnimationNode

class TransformObjectNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_TransformObjectNode"
    bl_label = "Transform Object"

    def create(self):
        self.inputs.new("an_ObjectSocket", "Object", "object").defaultDrawType = "PROPERTY_ONLY"
        self.inputs.new("an_MatrixSocket", "Matrix", "matrix")
        self.outputs.new("an_ObjectSocket", "Object", "object")

    def getExecutionCode(self):
        return "if object: object.matrix_world = matrix * object.matrix_world"
