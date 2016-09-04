import bpy
from bpy.props import *
from ... tree_info import keepNodeState
from ... base_types import AnimationNode

operationItems = [
    ("ADD", "Add", "", "", 0),
    ("SUBTRACT", "Subtract", "", "", 1),
    ("MULTIPLY", "Multiply", "Multiply element by element", "", 2),
    ("DIVIDE", "Divide", "Divide element by element", "", 3),
    ("CROSS", "Cross Product", "Calculate the cross/vector product, yielding a vector that is orthogonal to both input vectors", "", 4),
    ("PROJECT", "Project", "Projection of A on B, the parallel projection vector", "", 5),
    ("REFLECT", "Reflect", "Reflection of A from mirror B, the reflected vector", "", 6),
    ("NORMALIZE", "Normalize", "Scale the vector to a specific length", "", 7),
    ("SCALE", "Scale", "", "", 8),
    ("ABSOLUTE", "Absolute", "", "", 9),
    ("SNAP", "Snap", "Snap the vector to a point on a 3d grid", "", 10) ]

operationLabels = {
    "ADD" : "A + B",
    "SUBTRACT" : "A - B",
    "MULTIPLY" : "A * B",
    "DIVIDE" : "A / B",
    "CROSS" : "A x B",
    "PROJECT" : "A project B",
    "REFLECT" : "A reflect B",
    "NORMALIZE" : "normalize A",
    "SCALE" : "A * scale",
    "ABSOLUTE" : "abs A",
    "SNAP" : "snap A" }

searchItems = {
    "Add Vectors" : "ADD",
    "Subtract Vectors" : "SUBTRACT",
    "Multiply Vectors" : "MULTIPLY",
    "Normalize Vector" : "NORMALIZE",
    "Scale Vector" : "SCALE" }

operationsWithFloat = ["NORMALIZE", "SCALE"]
operationsWithSecondVector = ["ADD", "SUBTRACT", "MULTIPLY", "DIVIDE", "CROSS", "PROJECT", "REFLECT"]
operationsWithStepVector = ["SNAP"]

class VectorMathNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_VectorMathNode"
    bl_label = "Vector Math"
    dynamicLabelType = "HIDDEN_ONLY"

    @classmethod
    def getSearchTags(cls):
        for name, operation in searchItems.items():
            yield name, {"operation" : repr(operation)}

    def operationChanged(self, context):
        self.createInputs()

    operation = EnumProperty(name = "Operation", items = operationItems, default = "ADD", update = operationChanged)

    def create(self):
        self.createInputs()
        self.newOutput("Vector", "Result", "result")

    def draw(self, layout):
        layout.prop(self, "operation", text = "")

    def drawLabel(self):
        return operationLabels[self.operation]

    @keepNodeState
    def createInputs(self):
        self.inputs.clear()
        self.newInput("Vector", "A", "a")
        if self.operation in operationsWithSecondVector:
            self.newInput("Vector", "B", "b")
        if self.operation in operationsWithFloat:
            self.newInput("Float", "Scale", "scale").value = 1.0
        if self.operation in operationsWithStepVector:
            self.newInput("Vector", "Step Size", "stepSize").value = (0.1, 0.1, 0.1)


    def getExecutionCode(self):
        op = self.operation
        if op == "ADD": yield "result = a + b"
        elif op == "SUBTRACT": yield "result = a - b"
        elif op == "MULTIPLY": yield "result = mathutils.Vector((a[0] * b[0], a[1] * b[1], a[2] * b[2]))"
        elif op == "CROSS": yield "result = a.cross(b)"
        elif op == "DIVIDE":
            yield "result = mathutils.Vector((0, 0, 0))"
            yield "if b.x != 0: result.x = a.x / b.x"
            yield "if b.y != 0: result.y = a.y / b.y"
            yield "if b.z != 0: result.z = a.z / b.z"
        elif op == "PROJECT": yield "result = a.project(b)"
        elif op == "REFLECT": yield "result = a.reflect(b)"
        elif op == "NORMALIZE": yield "result = a.normalized() * scale"
        elif op == "SCALE": yield "result = a * scale"
        elif op == "ABSOLUTE": yield "result = mathutils.Vector((abs(a.x), abs(a.y), abs(a.z)))"
        elif op == "SNAP":
            yield "result = a.copy()"
            yield "if stepSize.x != 0: result.x = round(a.x / stepSize.x) * stepSize.x"
            yield "if stepSize.y != 0: result.y = round(a.y / stepSize.y) * stepSize.y"
            yield "if stepSize.z != 0: result.z = round(a.z / stepSize.z) * stepSize.z"


    def getUsedModules(self):
        return ["mathutils"]
