import bpy
from ... base_types.node import AnimationNode

class DecomposeMatrixNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_DecomposeMatrixNode"
    bl_label = "Decompose Matrix"

    def create(self):
        self.inputs.new("an_MatrixSocket", "Matrix", "matrix")
        self.outputs.new("an_VectorSocket", "Translation", "translation")
        self.outputs.new("an_VectorSocket", "Rotation", "rotation")
        self.outputs.new("an_VectorSocket", "Scale", "scale")

    def getExecutionCode(self):
        isLinked = self.getLinkedOutputsDict()
        lines = []
        if isLinked["translation"]: lines.append("translation = matrix.to_translation()")
        if isLinked["rotation"]: lines.append("rotation = mathutils.Vector((matrix.to_euler()))")
        if isLinked["scale"]: lines.append("scale = matrix.to_scale()")
        return lines

    def getUsedModules(self):
        return ["mathutils"]
