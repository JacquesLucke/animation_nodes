import bpy
import math
from bpy.props import *
from ... tree_info import keepNodeLinks
from ... events import executionCodeChanged
from ... base_types.node import AnimationNode

operationItems = [
    ("ADD", "Add", "A + B", "", 0),
    ("SUBTRACT", "Subtract", "A - B", "", 1),
    ("MULTIPLY", "Multiply", "A * B", "", 2),
    ("DIVIDE", "Divide", "A / B", "", 3),
    ("SINE", "Sine", "sin A", "", 4),
    ("COSINE", "Cosine", "cos A", "", 5),
    ("TANGENT", "Tangent", "tan A", "", 6),
    ("ARCSINE", "Arcsine", "asin A", "", 7),
    ("ARCCOSINE", "Arccosine", "acos A", "", 8),
    ("ARCTANGENT", "Arctangent", "atan A", "", 9),
    ("POWER", "Power", "A ** B", "", 10),
    ("LOGARITHM", "Logarithm", "log A, base B", "", 11),
    ("MINIMUM", "Minimum", "min(A, B)", "", 12),
    ("MAXIMUM", "Maximum", "max(A, B)", "", 13),
    ("MODULO", "Modulo", "A mod B", "", 15),
    ("ABSOLUTE", "Absolute", "abs A", "", 16),
    ("FLOOR", "Floor", "floor A", "", 17),
    ("CEILING", "Ceiling", "ceil A", "", 18),
    ("SQRT", "Square Root", "sqrt A", "", 19),
    ("INVERT", "Invert", "- A", "", 20),
    ("RECIPROCAL", "Reciprocal", "1 / A", "", 21)]

singleInputOperations = ("SINE", "COSINE", "TANGENT", "ARCSINE",
    "ARCCOSINE", "ARCTANGENT", "ABSOLUTE", "FLOOR", "CEILING", "SQRT", "INVERT", "RECIPROCAL")

operationLabels = {item[0] : item[2] for item in operationItems}

searchItems = {
    "Add Numbers" : "ADD",
    "Subtract Numbers" : "SUBTRACT",
    "Multiply Numbers" : "MULTIPLY",
    "Divide Numbers" : "DIVIDE",
    "Invert Number" : "INVERT",
    "Reciprocal Number" : "RECIPROCAL" }


class FloatMathNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_FloatMathNode"
    bl_label = "Math"

    @classmethod
    def getSearchTags(cls):
        tags = []
        for name, operation in searchItems.items():
            tags.append((name, {"operation" : repr(operation)}))
        return tags

    def operationChanged(self, context):
        self.recreateInputSockets()
        executionCodeChanged()

    operation = EnumProperty(name = "Operation", default = "MULTIPLY",
        items = operationItems, update = operationChanged)

    def create(self):
        self.outputs.new("an_FloatSocket", "Result", "result")
        self.recreateInputSockets()

    def draw(self, layout):
        layout.prop(self, "operation", text = "")

    def drawLabel(self):
        label = operationLabels[self.operation]
        if getattr(self.socketA, "isUnlinked", False):
            label = label.replace("A", str(round(self.socketA.value, 4)))
        if getattr(self.socketB, "isUnlinked", False):
            label = label.replace("B", str(round(self.socketB.value, 4)))
        return label

    def edit(self):
        output = self.outputs[0]
        if output.dataType == "Float":
            if output.shouldBeIntegerSocket(): self.setOutputType("an_IntegerSocket")
        else:
            if output.shouldBeFloatSocket(): self.setOutputType("an_FloatSocket")

    def getExecutionCode(self):
        op = self.operation
        if op == "ADD": yield "result = a + b"
        if op == "SUBTRACT": yield "result = a - b"
        if op == "MULTIPLY": yield "result = a * b"
        if op == "DIVIDE": yield from ("if b == 0: result = 0",
                                       "else: result = a / b")
        if op == "SINE": yield "result = math.sin(a)"
        if op == "COSINE": yield "result = math.cos(a)"
        if op == "TANGENT": yield "result = math.tan(a)"
        if op == "ARCSINE": yield "result = math.asin(min(max(a, -1), 1))"
        if op == "ARCCOSINE": yield "result = math.acos(min(max(a, -1), 1))"
        if op == "ARCTANGENT": yield "result = math.atan(a)"
        if op == "POWER": yield "result = math.pow(a, b) if a >= 0 or int(b) == b else 0"
        if op == "LOGARITHM": yield from ("if a <= 0: result = 0",
                                          "elif b <= 0 or b == 1: result = math.log(a)",
                                          "else: result = math.log(a, b)")
        if op == "MINIMUM": yield "result = min(a, b)"
        if op == "MAXIMUM": yield "result = max(a, b)"
        if op == "LESSTHAN": yield "result = a < b"
        if op == "GREATHERTHAN": yield "result = a > b"
        if op == "ABSOLUTE": yield "result = abs(a)"
        if op == "MODULO": yield from ("if b == 0: result = 0",
                                       "else: result = a % b")
        if op == "FLOOR": yield "result = math.floor(a)"
        if op == "CEILING": yield "result = math.ceil(a)"
        if op == "SQRT": yield "result = math.sqrt(a) if a >= 0 else 0"
        if op == "INVERT": yield "result = - a"
        if op == "RECIPROCAL": yield "result = 1 / a if a != 0 else 0"

        if self.outputs[0].dataType == "Integer":
            yield "result = int(result)"

    def getUsedModules(self):
        return ["math"]

    def setOutputType(self, idName):
        if self.outputs[0].bl_idname == idName: return
        self._setOutputType(idName)

    @keepNodeLinks
    def _setOutputType(self, idName):
        self.outputs.clear()
        self.outputs.new(idName, "Result", "result")

    @keepNodeLinks
    def recreateInputSockets(self):
        defaultA = getattr(self.socketA, "value", 0)
        defaultB = getattr(self.socketB, "value", 1)

        self.inputs.clear()
        self.inputs.new("an_FloatSocket", "A", "a").value = defaultA
        if self.operation not in singleInputOperations:
            self.inputs.new("an_FloatSocket", "B", "b").value = defaultB

    @property
    def socketA(self):
        return self.inputs.get("A")

    @property
    def socketB(self):
        return self.inputs.get("B")
