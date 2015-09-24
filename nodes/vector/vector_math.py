import bpy
from bpy.props import *
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
    ("SCALE", "Scale", "A * scale", "", 8) ]

operationsWithFloat = ["NORMALIZE", "SCALE"]

operationLabels = {item[0] : item[2][:11] for item in operationItems}

class VectorMathNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_VectorMathNode"
    bl_label = "Vector Math"

    def operationChanged(self, context):
        self.inputs["B"].hide = self.operation in operationsWithFloat
        self.inputs["Scale"].hide = self.operation not in operationsWithFloat
        executionCodeChanged()

    operation = EnumProperty(name = "Operation", items = operationItems, default = "ADD", update = operationChanged)

    def create(self):
        self.inputs.new("an_VectorSocket", "A", "a")
        self.inputs.new("an_VectorSocket", "B", "b")
        socket = self.inputs.new("an_FloatSocket", "Scale", "scale")
        socket.hide = True
        socket.value = 1.0
        self.outputs.new("an_VectorSocket", "Result", "result")

    def draw(self, layout):
        layout.prop(self, "operation", text = "")

    def drawLabel(self):
        return operationLabels[self.operation]

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

    def getUsedModules(self):
        return ["mathutils"]
