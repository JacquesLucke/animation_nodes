import bpy
from bpy.props import *
from ... events import executionCodeChanged
from ... base_types.node import AnimationNode

operationItems = [
    ("AND", "A and B", "", "NONE", 0),
    ("NAND", "not (A and B)", "", "NONE", 1),
    ("OR", "A or B", "", "NONE", 2),
    ("NOR", "not (A or B)", "", "NONE", 3),
    ("XOR", "A xor B", "A must be different than B", "NONE", 4) ]

class LogicOperatorsNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_LogicOperatorsNode"
    bl_label = "Logic Operators"

    operation = EnumProperty(name = "Operation", default = "AND",
        items = operationItems, update = executionCodeChanged)

    def create(self):
        self.inputs.new("an_BooleanSocket", "A", "a")
        self.inputs.new("an_BooleanSocket", "B", "b")
        self.outputs.new("an_BooleanSocket", "Result", "result")

    def draw(self, layout):
        layout.prop(self, "operation", text = "")

    def getExecutionCode(self):
        op = self.operation
        if op == "AND": return "result = a and b"
        if op == "NAND": return "result = not (a and b)"
        if op == "OR": return "result = a or b"
        if op == "NOR": return "result = not (a or b)"
        if op == "XOR": return "result = a ^ b"
