import bpy
import math
from bpy.props import *
from ... tree_info import keepNodeState
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
    ("RECIPROCAL", "Reciprocal", "1 / A", "", 21),
    ("SNAP", "Snap", "snap A to Step ", "", 22),
    ("ARCTANGENT2", "Arctangent B/A", "atan2 (B / A)", "", 23),
    ("HYPOTENUSE", "Hypotenuse", "hypot A, B", "", 24),
    ("COPY_SIGN", "Copy Sign", "A sign of B", "", 25)]

secondInputOperations = ("ADD", "SUBTRACT", "MULTIPLY", "DIVIDE", "POWER",
    "MINIMUM", "MAXIMUM", "MODULO", "ARCTANGENT2", "HYPOTENUSE", "COPY_SIGN")
baseInputOperations = ("LOGARITHM", )
stepSizeInputOperations = ("SNAP", )

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
    dynamicLabelType = "HIDDEN_ONLY"

    @classmethod
    def getSearchTags(cls):
        tags = []
        for name, operation in searchItems.items():
            tags.append((name, {"operation" : repr(operation)}))
        return tags

    def operationChanged(self, context):
        self.recreateInputSockets()

    operation = EnumProperty(name = "Operation", default = "MULTIPLY",
        items = operationItems, update = operationChanged)

    def create(self):
        self.newOutput("Float", "Result", "result")
        self.recreateInputSockets()

    def draw(self, layout):
        row = layout.row(align = True)
        row.prop(self, "operation", text = "")
        self.invokePopup(row, "drawOperationChooser", icon = "SCRIPTWIN")

    def drawLabel(self):
        label = operationLabels[self.operation]
        if getattr(self.socketA, "isUnlinked", False):
            label = label.replace("A", str(round(self.socketA.value, 4)))

        if getattr(self.socketB, "isUnlinked", False):
            label = label.replace("B", str(round(self.socketB.value, 4)))
        if getattr(self.socketBase, "isUnlinked", False):
            label = label.replace("B", str(round(self.socketBase.value, 4)))
        if getattr(self.socketStep, "isUnlinked", False):
            label = label.replace("Step", str(round(self.socketStep.value, 4)))

        return label

    def edit(self):
        output = self.outputs[0]
        if output.dataType == "Float":
            if output.shouldBeIntegerSocket(): self.setOutputType("Integer")
        else:
            if output.shouldBeFloatSocket(): self.setOutputType("Float")

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
        if op == "ARCTANGENT2": yield "result = math.atan2(b, a)"
        if op == "HYPOTENUSE": yield "result = math.hypot(a, b)"
        if op == "POWER": yield "result = math.pow(a, b) if a >= 0 or int(b) == b else 0"
        if op == "LOGARITHM":
            if "Base" not in self.inputs: yield "base = b" # to keep older files working
            yield "if a <= 0: result = 0"
            yield "elif base <= 0 or base == 1: result = math.log(a)"
            yield "else: result = math.log(a, base)"
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
        if op == "COPY_SIGN": yield "result = math.copysign(a, b)"
        if op == "INVERT": yield "result = - a"
        if op == "RECIPROCAL": yield "result = 1 / a if a != 0 else 0"
        if op == "SNAP": yield "result = round(a / stepSize) * stepSize if stepSize != 0 else a"

        if self.outputs[0].dataType == "Integer":
            yield "result = int(result)"

    def getUsedModules(self):
        return ["math"]

    def setOutputType(self, dataType):
        if self.outputs[0].dataType != dataType:
            self._setOutputType(dataType)

    @keepNodeState
    def _setOutputType(self, dataType):
        self.outputs.clear()
        self.newOutput(dataType, "Result", "result")

    @keepNodeState
    def recreateInputSockets(self):
        self.inputs.clear()

        self.newInput("Float", "A", "a")
        if self.operation in secondInputOperations:
            self.newInput("Float", "B", "b").value = 1
        if self.operation in baseInputOperations:
            self.newInput("Float", "Base", "base")
        if self.operation in stepSizeInputOperations:
            self.newInput("Float", "Step Size", "stepSize")

    @property
    def socketA(self):
        return self.inputs.get("A")

    @property
    def socketB(self):
        return self.inputs.get("B")

    @property
    def socketBase(self):
        return self.inputs.get("Base")

    @property
    def socketStep(self):
        return self.inputs.get("Step Size")

    def drawOperationChooser(self, layout):
        row = layout.row()

        col = row.column()
        subcol = col.column(align = True)
        self.operationButton(subcol, "ADD", "Add")
        self.operationButton(subcol, "SUBTRACT", "Subtract")
        self.operationButton(subcol, "MULTIPLY", "Multiply")
        self.operationButton(subcol, "DIVIDE", "Divide")
        self.operationButton(subcol, "MODULO", "Modulo")
        subcol = col.column(align = True)
        self.operationButton(subcol, "INVERT", "Invert")
        self.operationButton(subcol, "RECIPROCAL", "Reciprocal")
        self.operationButton(subcol, "COPY_SIGN", "Copy Sign")

        col = row.column()
        subcol = col.column(align = True)
        self.operationButton(subcol, "POWER", "Power")
        self.operationButton(subcol, "LOGARITHM", "Logarithm")
        self.operationButton(subcol, "SQRT", "Square Root")
        subcol = col.column(align = True)
        self.operationButton(subcol, "ABSOLUTE", "Absolute")
        self.operationButton(subcol, "MINIMUM", "Minimum")
        self.operationButton(subcol, "MAXIMUM", "Maximum")
        self.operationButton(subcol, "FLOOR", "Floor")
        self.operationButton(subcol, "CEILING", "Ceiling")
        self.operationButton(subcol, "SNAP", "Snap")

        col = layout.column(align = True)
        row = col.row(align = True)
        self.operationButton(row, "SINE", "Sine")
        self.operationButton(row, "ARCSINE", "Arcsine")
        row = col.row(align = True)
        self.operationButton(row, "COSINE", "Cosine")
        self.operationButton(row, "ARCCOSINE", "Arccosine")
        row = col.row(align = True)
        self.operationButton(row, "TANGENT", "Tangent")
        self.operationButton(row, "ARCTANGENT", "Arctangent")
        self.operationButton(row, "ARCTANGENT2", "Arctangent B/A")
        self.operationButton(col, "HYPOTENUSE", "Hypotenuse")

    def operationButton(self, layout, operation, text):
        self.invokeFunction(layout, "setOperation", text = text, data = operation)

    def setOperation(self, operation):
        self.operation = operation
