import bpy
from ... base_types.node import AnimationNode

class TranslationMatrixNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_TranslationMatrixNode"
    bl_label = "Translation Matrix"

    def create(self):
        self.newInput("Vector", "Translation", "translation")
        self.newOutput("Matrix", "Matrix", "matrix")

    def getExecutionCode(self):
        return "matrix = Matrix.Translation(translation)"
