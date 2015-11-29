import bpy
from bpy.props import *
from ... tree_info import keepNodeLinks
from ... events import executionCodeChanged
from ... base_types.node import AnimationNode

operationItems = [
    ("ADD", "Add", "A + B", "", 0),
    ("SUBTRACT", "Subtract", "A - B", "", 1),
    ("MULTIPLY", "Multiply", "A * B       Multiply element by element", "", 2),
    ("DIVIDE", "Divide", "A / B       Divide element by element", "", 3),
    ("CROSS", "Cross Product", "A cross B   Calculate the cross/vector product, yielding a vector that is orthogonal to both input vectors", "", 4),
    ("PROJECT", "Project", "A project B  Projection of A on B, the parallel projection vector", "", 5),
    ("REFLECT", "Reflect", "A reflect B  Reflection of A from mirror B, the reflected vector", "", 6),
    ("NORMALIZE", "Normalize", "A normalize Scale the vector to a length of 1", "", 7),
    ("SCALE", "Scale", "A * scale", "", 8),
    ("ABSOLUTE", "Absolute", "abs A", "", 9) ]

operationsWithFloat = ["NORMALIZE", "SCALE"]
operationsWithVector = ["ADD", "SUBTRACT", "MULTIPLY", "DIVIDE", "CROSS", "PROJECT", "REFLECT"]

operationLabels = {item[0] : item[2][:11] for item in operationItems}

searchItems = {
    "Add Vectors" : "ADD",
    "Subtract Vectors" : "SUBTRACT",
    "Multiply Vectors" : "MULTIPLY",
    "Normalize Vector" : "NORMALIZE",
    "Scale Vector" : "SCALE" }

class VectorMathNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_VectorMathNode"
    bl_label = "Vector Math"

    @classmethod
    def getSearchTags(cls):
        for name, operation in searchItems.items():
            yield name, {"operation" : repr(operation)}

    def operationChanged(self, context):
        self.createInputs()

    operation = EnumProperty(name = "Operation", items = operationItems, default = "ADD", update = operationChanged)

    def create(self):
        self.createInputs()
        self.outputs.new("an_VectorSocket", "Result", "result")

    def draw(self, layout):
        layout.prop(self, "operation", text = "")

    def drawLabel(self):
        return operationLabels[self.operation]

    @keepNodeLinks
    def createInputs(self):
        self.inputs.clear()
        self.inputs.new("an_VectorSocket", "A", "a")
        if self.operation in operationsWithVector:
            self.inputs.new("an_VectorSocket", "B", "b")
        if self.operation in operationsWithFloat:
            self.inputs.new("an_FloatSocket", "Scale", "scale").value = 1.0


    def getExecutionCode(self):
        op = self.operation
        if op == "ADD": return "result = a + b"
        elif op == "SUBTRACT": return "result = a - b"
        elif op == "MULTIPLY": return "result = mathutils.Vector((a[0] * b[0], a[1] * b[1], a[2] * b[2]))"
        elif op == "CROSS": return "result = a.cross(b)"
        elif op == "DIVIDE": return ("result = mathutils.Vector((0, 0, 0))",
                                     "if b[0] != 0: result[0] = a[0] / b[0]",
                                     "if b[1] != 0: result[1] = a[1] / b[1]",
                                     "if b[2] != 0: result[2] = a[2] / b[2]")
        elif op == "PROJECT": return "result = a.project(b)"
        elif op == "REFLECT": return "result = a.reflect(b)"
        elif op == "NORMALIZE": return "result = a.normalized() * scale"
        elif op == "SCALE": return "result = a * scale"
        elif op == "ABSOLUTE": return "result = mathutils.Vector((abs(a.x), abs(a.y), abs(a.z)))"

    def getUsedModules(self):
        return ["mathutils"]
