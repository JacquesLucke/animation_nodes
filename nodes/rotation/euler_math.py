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

class EulerMathNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_EulerMathNode"
    bl_label = "Euler Math"

    def operationChanged(self, context):
        self.createInputs()

    operation = EnumProperty(name = "Operation", items = operationItems, default = "ADD", update = operationChanged)

    def create(self):
        self.createInputs()
        self.outputs.new("an_EulerSocket", "Result", "result")

    def draw(self, layout):
        layout.prop(self, "operation", text = "")

    def drawLabel(self):
        return operationLabels[self.operation]

    @keepNodeState
    def createInputs(self):
        self.inputs.clear()
        self.inputs.new("an_EulerSocket", "A", "a")
        if self.operation in operationsWithSecondEuler:
            self.inputs.new("an_EulerSocket", "B", "b")
        if self.operation in operationsWithFloat:
            self.inputs.new("an_FloatSocket", "Scale", "scale").value = 1.0
        if self.operation in operationsWithStepEuler:
            self.inputs.new("an_EulerSocket", "Step Size", "stepSize").value = (0.1, 0.1, 0.1)


    def getExecutionCode(self):
        op = self.operation
        yield "v1 = mathutils.Vector((a))"
        if self.operation in operationsWithSecondEuler:
            yield "v2 = mathutils.Vector((b))"

        if op == "ADD": yield "_result = v1 + v2"
        elif op == "SUBTRACT": yield "_result = v1 - v2"
        elif op == "MULTIPLY": yield "_result = mathutils.Vector((v1[0] * v2[0], v1[1] * v2[1], v1[2] * v2[2]))"
        elif op == "DIVIDE":
            yield "_result = mathutils.Vector((0, 0, 0))"
            yield "if v2.x != 0: _result.x = v1.x / v2.x"
            yield "if v2.y != 0: _result.y = v1.y / v2.y"
            yield "if v2.z != 0: _result.z = v1.z / v2.z"
        elif op == "SCALE": yield "_result = v1 * scale"
        elif op == "ABSOLUTE": yield "_result = mathutils.Vector((abs(v1.x), abs(v1.y), abs(v1.z)))"
        elif op == "SNAP":
            yield "_result = mathutils.Vector((0, 0, 0))"
            yield "if stepSize.x != 0: _result.x = round(v1.x / stepSize.x) * stepSize.x"
            yield "if stepSize.y != 0: _result.y = round(v1.y / stepSize.y) * stepSize.y"
            yield "if stepSize.z != 0: _result.z = round(v1.z / stepSize.z) * stepSize.z"

        yield "result = mathutils.Euler(_result)"


    def getUsedModules(self):
        return ["mathutils"]
