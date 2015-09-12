import bpy
from ... base_types.node import AnimationNode


class ObjectMatrixInputNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_ObjectMatrixInputNode"
    bl_label = "Object Matrix Input"

    def create(self):
        self.inputs.new("an_ObjectSocket", "Object", "object").defaultDrawType = "PROPERTY_ONLY"
        self.outputs.new("an_MatrixSocket", "World", "world")
        self.outputs.new("an_MatrixSocket", "Basis", "basis").hide = True
        self.outputs.new("an_MatrixSocket", "Local", "local").hide = True
        self.outputs.new("an_MatrixSocket", "Parent Inverse", "parentInverse").hide = True

    def getExecutionCode(self):

        isLinked = self.getLinkedOutputsDict()
        if not any(isLinked.values()): return ""
        lines = []
        lines.append("if object is None:")
        if isLinked["world"]: lines.append("    world = mathutils.Matrix.Identity(4)")
        if isLinked["basis"]: lines.append("    basis = mathutils.Matrix.Identity(4)")
        if isLinked["local"]: lines.append("    local = mathutils.Matrix.Identity(4)")
        if isLinked["parentInverse"]: lines.append("    parentInverse = mathutils.Matrix.Identity(4)")
        lines.append("else:")
        if isLinked["world"]: lines.append("    world = object.matrix_world")
        if isLinked["basis"]: lines.append("    basis = object.matrix_basis")
        if isLinked["local"]: lines.append("    local = object.matrix_local")
        if isLinked["parentInverse"]: lines.append("    parentInverse = object.matrix_parent_inverse")

        return lines

    def getUsedModules(self):
        return ["mathutils"]
