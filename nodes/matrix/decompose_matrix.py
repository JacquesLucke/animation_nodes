import bpy
from ... base_types.node import AnimationNode

class DecomposeMatrix(bpy.types.Node, AnimationNode):
    bl_idname = "mn_DecomposeMatrix"
    bl_label = "Decompose Matrix"
    isDetermined = True

    inputNames = { "Matrix" : "matrix" }

    outputNames = { "Translation" : "translation",
                    "Rotation" : "rotation",
                    "Scale" : "scale" }

    def create(self):
        self.inputs.new("mn_MatrixSocket", "Matrix")
        self.outputs.new("mn_VectorSocket", "Translation")
        self.outputs.new("mn_VectorSocket", "Rotation")
        self.outputs.new("mn_VectorSocket", "Scale")

    def getExecutionCode(self, usedOutputs):
        codeLines = []
        if usedOutputs["Translation"]: codeLines.append("$translation$ = %matrix%.to_translation()")
        if usedOutputs["Rotation"]: codeLines.append("$rotation$ = mathutils.Vector((%matrix%.to_euler()))")
        if usedOutputs["Scale"]: codeLines.append("$scale$ = %matrix%.to_scale()")
        return "\n".join(codeLines)

    def getModuleList(self):
        return ["mathutils"]
