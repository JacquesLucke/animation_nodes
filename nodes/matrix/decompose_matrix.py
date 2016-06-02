import bpy
from ... base_types.node import AnimationNode

class DecomposeMatrixNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_DecomposeMatrixNode"
    bl_label = "Decompose Matrix"

    def create(self):
        self.newInput("Matrix", "Matrix", "matrix")
        self.newOutput("Vector", "Translation", "translation")
        self.newOutput("Euler", "Rotation", "rotation")
        self.newOutput("Vector", "Scale", "scale")

    def getExecutionCode(self):
        isLinked = self.getLinkedOutputsDict()
        if isLinked["translation"]: yield "translation = matrix.to_translation()"
        if isLinked["rotation"]:    yield "rotation = matrix.to_euler()"
        if isLinked["scale"]:       yield "scale = matrix.to_scale()"
