import bpy
from bpy.props import *
from ... events import executionCodeChanged
from ... base_types.node import AnimationNode

operationItems = [
    ("ADD", "Add", "", "", 0),
    ("MULTIPLY", "Multiply", "", "", 1),
    ("MIN", "Min", "", "", 2),
    ("MAX", "Max", "", "", 3),
    ("AVERAGE", "Average", "", "", 4) ]

class NumberListMathNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_NumberListMathNode"
    bl_label = "Number List Math"

    operation = EnumProperty(name = "Operation", default = "ADD",
        items = operationItems, update = executionCodeChanged)

    def create(self):
        self.newInput("an_FloatListSocket", "Number List", "numbers")
        self.newOutput("an_FloatSocket", "Result", "result")

    def draw(self, layout):
        layout.prop(self, "operation", text = "")

    def getExecutionCode(self):
        if self.operation in ("ADD", "AVERAGE"): yield "result = functools.reduce(operator.add, numbers, 0)"
        if self.operation == "MULTIPLY": yield "result = functools.reduce(operator.mul, numbers, 1)"
        if self.operation == "MIN": yield "result = min(numbers) if len(numbers) > 0 else 0"
        if self.operation == "MAX": yield "result = max(numbers) if len(numbers) > 0 else 0"
        if self.operation == "AVERAGE": yield "if len(numbers) > 0: result /= len(numbers)"

    def getUsedModules(self):
        return ["operator", "functools"]
