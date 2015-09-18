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
    ("LOGARITHM", "Logarithm", "A log B", "", 11),
    ("MINIMUM", "Minimum", "min A B", "", 12),
    ("MAXIMUM", "Maximum", "max A B", "", 13),
    ("ROUND", "Round", "A round B", "", 14),
    ("MODULO", "Modulo", "A % B", "", 15),
    ("ABSOLUTE", "Absolute", "abs A", "", 16),
    ("FLOOR", "Floor", "floor A", "", 17),
    ("CEILING", "Ceiling", "ceil A", "", 18),
    ("SQRT", "Square Root", "sqrt A", "", 19),
    ("INVERT", "Invert", "- A", "", 20),
    ("RECIPROCAL", "Reciprocal", "1 / A", "", 21)]

singleInputOperations = ("SINE", "COSINE", "TANGENT", "ARCSINE",
    "ARCCOSINE", "ARCTANGENT", "ABSOLUTE", "FLOOR", "CEILING", "SQRT", "INVERT", "RECIPROCAL")

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
        for item in operationItems:
            if item[0] == self.operation:
                self.operationLabel = item[2]
        self.inputs[1].hide = self.operation in singleInputOperations
        executionCodeChanged()

    def outputIntegerChanged(self, context):
        self.recreateOutputSocket()

    operation = EnumProperty(name = "Operation", default = "MULTIPLY",
        items = operationItems, update = operationChanged)

    outputInteger = BoolProperty(name = "Output Integer", default = False,
        update = outputIntegerChanged)

    operationLabel = StringProperty(name = "Operation Label", default = "A * B")

    def create(self):
        self.inputs.new("an_FloatSocket", "A", "a")
        self.inputs.new("an_FloatSocket", "B", "b").value = 1.0
        self.outputs.new("an_FloatSocket", "Result", "result")

    def draw(self, layout):
        layout.prop(self, "operation", text = "")

    def drawLabel(self):
        return "{} ({})".format(self.operationLabel, "Integer" if self.outputInteger else "Float")

    def edit(self):
        targets = self.outputs[0].dataTargets
        if len(targets) >= 1:
            if all([target.dataType == "Integer" for target in targets]):
                self.outputInteger = True
            else:
                self.outputInteger = False
        elif self.outputInteger:
            self.outputInteger = False

    def recreateOutputSocket(self):
        idName = "an_IntegerSocket" if self.outputInteger else "an_FloatSocket"
        if self.outputs[0].bl_idname == idName: return
        self._recreateOutputSocket(idName)

    @keepNodeLinks
    def _recreateOutputSocket(self, idName):
        self.outputs.clear()
        self.outputs.new(idName, "Result", "result")

    def getExecutionCode(self):
        op = self.operation
        if op == "ADD": yield "result = a + b"
        if op == "SUBTRACT": yield "result = a - b"
        if op == "MULITPLY": yield "result = a * b"
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
        if op == "ROUND": yield "result = round(a, int(b))"
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

        if self.outputInteger:
            yield "result = int(result)"

    def getUsedModules(self):
        return ["math"]
