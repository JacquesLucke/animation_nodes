import bpy
from .... base_types import AnimationNode

class UpdateObjectMatricesNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_UpdateObjectMatricesNode"
    bl_label = "Update Object Matrices"

    def create(self):
        self.newInput("Object", "Object", "object").defaultDrawType = "PROPERTY_ONLY"
        self.newOutput("Object", "Object", "object")

    def getExecutionCode(self, required):
        yield "if object:"
        yield "    evaluatedObject = AN.utils.depsgraph.getEvaluatedID(object)"
        yield "    object.matrix_world = AN.utils.math.composeMatrix(evaluatedObject.location, evaluatedObject.rotation_euler, evaluatedObject.scale)"
