import bpy
from bpy.props import *
from ... tree_info import keepNodeState
from ... base_types.node import AnimationNode

operationItems = [
    ("ADD", "Add", "", "", 0),
    ("SUBTRACT", "Subtract", "", "", 1),
    ("MULTIPLY", "Multiply", "Multiply element by element (values are in radians internally)", "", 2),
    ("DIVIDE", "Divide", "Divide element by element (values are in radians internally)", "", 3),
    ("SCALE", "Scale", "", "", 4),
    ("ABSOLUTE", "Absolute", "", "", 5),
    ("SNAP", "Snap", "Snap the individual axis rotations", "", 6) ]

operationLabels = {
    "ADD" : "A + B",
    "SUBTRACT" : "A - B",
    "MULTIPLY" : "A * B",
    "DIVIDE" : "A / B",
    "SCALE" : "A * scale",
    "ABSOLUTE" : "abs A",
    "SNAP" : "snap A" }

operationsWithFloat = ["SCALE"]
operationsWithSecondEuler = ["ADD", "SUBTRACT", "MULTIPLY", "DIVIDE"]
operationsWithStepEuler = ["SNAP"]
operationsWithDegree = ["MULTIPLY", "DIVIDE"]

class EulerMathNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_EulerMathNode"
    bl_label = "Euler Math"
    dynamicLabelType = "HIDDEN_ONLY"

    def operationChanged(self, context):
        self.createInputs()

    operation = EnumProperty(name = "Operation", items = operationItems, default = "ADD", update = operationChanged)
    useDegree = BoolProperty(name = "Use Degrees",
        description = "Multiply and Divide degrees. If false, operation will use radians (output is always radians)",
        default = True, update = operationChanged)

    def create(self):
        self.createInputs()
        self.newOutput("an_EulerSocket", "Result", "result")

    def draw(self, layout):
        layout.prop(self, "operation", text = "")

    def drawAdvanced(self, layout):
        if self.operation in operationsWithDegree: layout.prop(self, "useDegree")

    def drawLabel(self):
        return operationLabels[self.operation]

    @keepNodeState
    def createInputs(self):
        self.inputs.clear()
        self.newInput("an_EulerSocket", "A", "a")
        if self.operation in operationsWithSecondEuler:
            self.newInput("an_EulerSocket", "B", "b")
        if self.operation in operationsWithFloat:
            self.newInput("an_FloatSocket", "Scale", "scale").value = 1.0
        if self.operation in operationsWithStepEuler:
            self.newInput("an_EulerSocket", "Step Size", "stepSize").value = (0.1, 0.1, 0.1)


    def getExecutionCode(self):
        op = self.operation

        if op == "ADD": return "result = mathutils.Euler((a[0] + b[0], a[1] + b[1], a[2] + b[2]), 'XYZ')"
        elif op == "SUBTRACT": return "result = mathutils.Euler((a[0] - b[0], a[1] - b[1], a[2] - b[2]), 'XYZ')"
        elif op == "MULTIPLY":
            if self.useDegree:
                return "result = mathutils.Euler((math.radians(math.degrees(A) * math.degrees(B)) for A, B in zip(a, b)), 'XYZ')"
            else: return "result = mathutils.Euler((a[0] * b[0], a[1] * b[1], a[2] * b[2]), 'XYZ')"
        elif op == "DIVIDE":
            if self.useDegree:
                return ("result = mathutils.Euler((0, 0, 0), 'XYZ')",
                        "if b[0] != 0: result[0] = math.radians(math.degrees(a[0]) / math.degrees(b[0]))",
                        "if b[1] != 0: result[1] = math.radians(math.degrees(a[1]) / math.degrees(b[1]))",
                        "if b[2] != 0: result[2] = math.radians(math.degrees(a[2]) / math.degrees(b[2]))")
            else:
                return ("result = mathutils.Euler((0, 0, 0), 'XYZ')",
                        "if b[0] != 0: result[0] = a[0] / b[0]",
                        "if b[1] != 0: result[1] = a[1] / b[1]",
                        "if b[2] != 0: result[2] = a[2] / b[2]")
        elif op == "SCALE":  return "result = mathutils.Euler((a[0] * scale, a[1] * scale, a[2] * scale), 'XYZ')"
        elif op == "ABSOLUTE": return "result = mathutils.Euler((abs(a[0]), abs(a[1]), abs(a[2])), 'XYZ')"
        elif op == "SNAP":
            return ("result = a.copy()",
                    "if stepSize.x != 0: result[0] = round(a[0] / stepSize[0]) * stepSize[0]",
                    "if stepSize.y != 0: result[1] = round(a[1] / stepSize[1]) * stepSize[1]",
                    "if stepSize.z != 0: result[2] = round(a[2] / stepSize[2]) * stepSize[2]")


    def getUsedModules(self):
        return ["math, mathutils"]
