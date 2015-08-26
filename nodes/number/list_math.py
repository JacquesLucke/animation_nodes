import bpy
from bpy.props import *
from ... events import executionCodeChanged
from ... base_types.node import AnimationNode

operationItems = [
    ("ADD", "Add", ""),
    ("MULTIPLY", "Multiply", ""),
    ("MIN", "Min", ""),
    ("MAX", "Max", "") ]

class ListMathNode(bpy.types.Node, AnimationNode):
    bl_idname = "ListMathNode"
    bl_label = "List Math"

    operation = EnumProperty(name = "Operation", items = operationItems, update = executionCodeChanged)

    def create(self):
        self.inputs.new("an_FloatListSocket", "Number List", "numbers")
        self.outputs.new("an_FloatSocket", "Result", "result")

    def draw(self, layout):
        layout.prop(self, "operation", text = "")

    def getExecutionCode(self):
        if self.operation == "ADD": return "result = functools.reduce(operator.add, numbers, 0)"
        if self.operation == "MULTIPLY": return "result = functools.reduce(operator.mul, numbers, 1)"
        if self.operation == "MIN": return "result = min(numbers) if len(numbers) > 0 else 0"
        if self.operation == "MAX": return "result = max(numbers) if len(numbers) > 0 else 0"

    def getModuleList(self):
        return ["operator", "functools"]
