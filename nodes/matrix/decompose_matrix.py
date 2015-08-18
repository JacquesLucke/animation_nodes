import bpy
from ... base_types.node import AnimationNode

class DecomposeMatrix(bpy.types.Node, AnimationNode):
    bl_idname = "an_DecomposeMatrix"
    bl_label = "Decompose Matrix"
    isDetermined = True

    def create(self):
        self.inputs.new("an_MatrixSocket", "Matrix", "matrix")
        self.outputs.new("an_VectorSocket", "Translation", "translation")
        self.outputs.new("an_VectorSocket", "Rotation", "rotation")
        self.outputs.new("an_VectorSocket", "Scale", "scale")

    def getExecutionCode(self, usedOutputs):
        lines = []
        if usedOutputs["Translation"]: lines.append("translation = matrix.to_translation()")
        if usedOutputs["Rotation"]: lines.append("rotation = mathutils.Vector((matrix.to_euler()))")
        if usedOutputs["Scale"]: lines.append("scale = matrix.to_scale()")
        return lines

    def getModuleList(self):
        return ["mathutils"]
