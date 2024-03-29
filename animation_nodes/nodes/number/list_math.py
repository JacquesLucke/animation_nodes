import bpy
from bpy.props import *
from ... events import executionCodeChanged
from ... base_types import AnimationNode

operationItems = [
    ("ADD", "Add", "", "", 0),
    ("MULTIPLY", "Multiply", "", "", 1),
    ("MIN", "Min", "", "", 2),
    ("MAX", "Max", "", "", 3),
    ("AVERAGE", "Average", "", "", 4) ]

class NumberListMathNode(AnimationNode, bpy.types.Node):
    bl_idname = "an_NumberListMathNode"
    bl_label = "Number List Math"
    searchTags = [(item[1] + " List Numbers", {"operation" : repr(item[0])}) for item in operationItems]

    operation: EnumProperty(name = "Operation", default = "ADD",
        items = operationItems, update = executionCodeChanged)

    def create(self):
        self.newInput("Float List", "Number List", "numbers")
        self.newOutput("Float", "Result", "result")
        if self.operation in ("MIN", "MAX"):
            self.newOutput("Integer", "Index", "index", hide = True)

    def draw(self, layout):
        layout.prop(self, "operation", text = "")

    def getExecutionCode(self, required):
        if self.operation == "ADD":
            yield "result = numbers.getSumOfElements()"
        elif self.operation == "MULTIPLY":
            yield "result = numbers.getProductOfElements()"
        elif self.operation == "MIN":
            yield "index = int(numpy.argmin(numbers.asNumpyArray())) if len(numbers) > 0 else 0"
            yield "result = numbers[index] if len(numbers) > 0 else 0"
        elif self.operation == "MAX":
            yield "index = int(numpy.argmax(numbers.asNumpyArray())) if len(numbers) > 0 else 0"
            yield "result = numbers[index] if len(numbers) > 0 else 0"
        elif self.operation == "AVERAGE":
            yield "result = numbers.getAverageOfElements() if len(numbers) > 0 else 0"

    def getUsedModules(self):
        return ["numpy"]
