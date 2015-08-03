import bpy
from ... base_types.node import AnimationNode


class ObjectMatrixInput(bpy.types.Node, AnimationNode):
    bl_idname = "mn_ObjectMatrixInput"
    bl_label = "Object Matrix Input"

    inputNames = { "Object" : "object" }

    outputNames = { "Basis" : "basis",
                    "Local" : "local",
                    "Parent Inverse" : "parentInverse",
                    "World" : "world" }

    def create(self):
        self.inputs.new("mn_ObjectSocket", "Object").showName = False
        self.outputs.new("mn_MatrixSocket", "Basis")
        self.outputs.new("mn_MatrixSocket", "Local")
        self.outputs.new("mn_MatrixSocket", "Parent Inverse")
        self.outputs.new("mn_MatrixSocket", "World")

    def getExecutionCode(self, usedOutputs):
        codeLines = []
        codeLines.append("try:")
        if usedOutputs["Basis"]: codeLines.append("    $basis$ = %object%.matrix_basis")
        if usedOutputs["Local"]: codeLines.append("    $local$ = %object%.matrix_local")
        if usedOutputs["Parent Inverse"]: codeLines.append("    $parentInverse$ = %object%.matrix_parent_inverse")
        if usedOutputs["World"]: codeLines.append("    $world$ = %object%.matrix_world")
        codeLines.append("    pass")
        codeLines.append("except:")
        codeLines.append("    $basis$ = mathutils.Matrix.Identity(4)")
        codeLines.append("    $local$ = mathutils.Matrix.Identity(4)")
        codeLines.append("    $parentInverse$ = mathutils.Matrix.Identity(4)")
        codeLines.append("    $world$ = mathutils.Matrix.Identity(4)")
        return "\n".join(codeLines)

    def getModuleList(self):
        return ["mathutils"]
