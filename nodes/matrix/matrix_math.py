import bpy
from bpy.props import *
from ... events import executionCodeChanged
from ... base_types.node import AnimationNode

operationItems = [("MULTIPLY", "Multiply", "")]

class MatrixMathNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_MatrixMathNode"
    bl_label = "Matrix Math"

    operation = EnumProperty(name = "Operation", items = operationItems, update = executionCodeChanged)

    def create(self):
        self.inputs.new("an_MatrixSocket", "A", "a")
        self.inputs.new("an_MatrixSocket", "B", "b")
        self.outputs.new("an_MatrixSocket", "Result", "result")

    def draw(self, layout):
        layout.prop(self, "operation", text = "")

    def getExecutionCode(self):
        if self.operation == "MULTIPLY":
            return "result = a * b"
