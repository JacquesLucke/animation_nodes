import bpy
from ... base_types.node import AnimationNode


class ObjectMatrixInput(bpy.types.Node, AnimationNode):
    bl_idname = "an_ObjectMatrixInput"
    bl_label = "Object Matrix Input"

    def create(self):
        self.inputs.new("an_ObjectSocket", "Object", "object").showName = False
        self.outputs.new("an_MatrixSocket", "Basis", "basis")
        self.outputs.new("an_MatrixSocket", "Local", "local")
        self.outputs.new("an_MatrixSocket", "Parent Inverse", "parentInverse")
        self.outputs.new("an_MatrixSocket", "World", "world")

    def getExecutionCode(self):
        usedOutputs = self.getUsedOutputsDict()
        lines = []
        lines.append("try:")
        if usedOutputs["basis"]: lines.append("    basis = object.matrix_basis")
        if usedOutputs["local"]: lines.append("    local = object.matrix_local")
        if usedOutputs["parentInverse"]: lines.append("    parentInverse = object.matrix_parent_inverse")
        if usedOutputs["world"]: lines.append("    world = object.matrix_world")
        lines.append("    pass")
        lines.append("except:")
        lines.append("    basis = mathutils.Matrix.Identity(4)")
        lines.append("    local = mathutils.Matrix.Identity(4)")
        lines.append("    parentInverse = mathutils.Matrix.Identity(4)")
        lines.append("    world = mathutils.Matrix.Identity(4)")
        return lines

    def getModuleList(self):
        return ["mathutils"]
