import bpy
from ... base_types.node import AnimationNode

class TranslationMatrixNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_TranslationMatrixNode"
    bl_label = "Translation Matrix"

    def create(self):
        self.newInput("an_VectorSocket", "Translation", "translation")
        self.newOutput("an_MatrixSocket", "Matrix", "matrix")

    def getExecutionCode(self):
        return "matrix = mathutils.Matrix.Translation(translation)"

    def getUsedModules(self):
        return ["mathutils"]
