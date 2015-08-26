import bpy
from ... base_types.node import AnimationNode


class ObjectMatrixInputNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_ObjectMatrixInputNode"
    bl_label = "Object Matrix Input"

    def create(self):
        self.inputs.new("an_ObjectSocket", "Object", "object").showName = False
        self.outputs.new("an_MatrixSocket", "Basis", "basis")
        self.outputs.new("an_MatrixSocket", "Local", "local")
        self.outputs.new("an_MatrixSocket", "Parent Inverse", "parentInverse")
        self.outputs.new("an_MatrixSocket", "World", "world")

    def getExecutionCode(self):
        if len(self.linkedOutputs) == 0: return ""

        usedOutputs = self.getUsedOutputsDict()
        lines = []
        lines.append("if object is None:")
        if usedOutputs["basis"]: lines.append("    basis = mathutils.Matrix.Identity(4)")
        if usedOutputs["local"]: lines.append("    local = mathutils.Matrix.Identity(4)")
        if usedOutputs["parentInverse"]: lines.append("    parentInverse = mathutils.Matrix.Identity(4)")
        if usedOutputs["world"]: lines.append("    world = mathutils.Matrix.Identity(4)")
        lines.append("else:")
        if usedOutputs["basis"]: lines.append("    basis = object.matrix_basis")
        if usedOutputs["local"]: lines.append("    local = object.matrix_local")
        if usedOutputs["parentInverse"]: lines.append("    parentInverse = object.matrix_parent_inverse")
        if usedOutputs["world"]: lines.append("    world = object.matrix_world")

        return lines

    def getModuleList(self):
        return ["mathutils"]
