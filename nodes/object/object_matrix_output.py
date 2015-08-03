import bpy
from ... events import executionCodeChanged
from ... base_types.node import AnimationNode

outputItems = [	("BASIS", "Basis", ""),
                ("LOCAL", "Local", ""),
                ("PARENT INVERSE", "Parent Inverse", ""),
                ("WORLD", "World", "") ]

class ObjectMatrixOutputNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_ObjectMatrixOutputNode"
    bl_label = "Object Matrix Output"

    inputNames = { "Object" : "object",
                   "Matrix" : "matrix" }

    outputNames = { "Object" : "object" }

    outputType = bpy.props.EnumProperty(items = outputItems, update = executionCodeChanged, default = "WORLD")

    def create(self):
        self.inputs.new("an_ObjectSocket", "Object").showName = False
        self.inputs.new("an_MatrixSocket", "Matrix")
        self.outputs.new("an_ObjectSocket", "Object")

    def draw_buttons(self, context, layout):
        layout.prop(self, "outputType", text = "Type")

    def getExecutionCode(self):
        t = self.outputType
        codeLines = []
        codeLines.append("if %object% is not None:")
        if t == "BASIS": codeLines.append("    %object%.matrix_basis = %matrix%")
        if t == "LOCAL": codeLines.append("    %object%.matrix_local = %matrix%")
        if t == "PARENT INVERSE": codeLines.append("    %object%.matrix_parent_inverse = %matrix%")
        if t == "WORLD": codeLines.append("    %object%.matrix_world = %matrix%")
        codeLines.append("$object$ = %object%")
        return "\n".join(codeLines)
