import bpy
from .... base_types.node import AnimationNode

class UpdateObjectMatricesNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_UpdateObjectMatricesNode"
    bl_label = "Update Object Matrices"

    def create(self):
        self.newInput("an_ObjectSocket", "Object", "object").defaultDrawType = "PROPERTY_ONLY"
        self.newOutput("an_ObjectSocket", "Object", "object")

    def getExecutionCode(self):
        yield "if object:"
        yield "    object.matrix_world = animation_nodes.utils.math.composeMatrix(object.location, object.rotation_euler, object.scale)"
