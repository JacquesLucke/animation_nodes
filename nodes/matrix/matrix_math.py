import bpy
from ... base_types.node import AnimationNode
from ... events import executionCodeChanged

operationItems = [("MULTIPLY", "Multiply", "")]

class MatrixMath(bpy.types.Node, AnimationNode):
    bl_idname = "an_MatrixMath"
    bl_label = "Matrix Math"
    isDetermined = True

    inputNames = { "A" : "a",
                   "B" : "b" }

    outputNames = { "Result" : "result" }

    operation = bpy.props.EnumProperty(name = "Operation", items = operationItems, update = executionCodeChanged)

    def create(self):
        self.inputs.new("an_MatrixSocket", "A")
        self.inputs.new("an_MatrixSocket", "B")
        self.outputs.new("an_MatrixSocket", "Result")

    def draw(self, layout):
        layout.prop(self, "operation", text = "")

    def getExecutionCode(self):
        if self.operation == "MULTIPLY":
            return "$result$ = %a% * %b%"
