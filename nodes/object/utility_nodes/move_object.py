import bpy
from .... base_types.node import AnimationNode

class MoveObjectNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_MoveObjectNode"
    bl_label = "Move Object"

    def create(self):
        self.newInput("an_ObjectSocket", "Object", "object").defaultDrawType = "PROPERTY_ONLY"
        self.newInput("an_VectorSocket", "Translation", "translation").defaultDrawType = "PROPERTY_ONLY"
        self.newOutput("an_ObjectSocket", "Object", "object")

    def getExecutionCode(self):
        return "if object: object.location += translation"
