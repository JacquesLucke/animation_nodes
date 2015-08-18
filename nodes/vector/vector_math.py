import bpy
from bpy.props import *
from ... events import executionCodeChanged
from ... base_types.node import AnimationNode

operationItems = [
    ("ADD", "Add", ""),
    ("SUBTRACT", "Subtract", ""),
    ("MULTIPLY", "Multiply", "Multiply element by element"),
    ("DIVIDE", "Divide", "Divide element by element"),
    ("CROSS", "Cross Product", "Calculate the cross/vector product, yielding a vector that is orthogonal to both input vectors") ]

class VectorMathNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_VectorMathNode"
    bl_label = "Vector Math"
    isDetermined = True

    operation = EnumProperty(name = "Operation", items = operationItems, default = "ADD", update = executionCodeChanged)

    def create(self):
        self.inputs.new("an_VectorSocket", "A", "a")
        self.inputs.new("an_VectorSocket", "B", "b")
        self.outputs.new("an_VectorSocket", "Result", "result")

    def draw(self, layout):
        layout.prop(self, "operation")

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

    def getModuleList(self):
        return ["mathutils"]
