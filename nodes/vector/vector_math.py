import bpy
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

    inputNames = { "A" : "a",
                   "B" : "b" }

    outputNames = { "Result" : "result" }

    operation = bpy.props.EnumProperty(name = "Operation", items = operationItems, default = "ADD", update = executionCodeChanged)

    def create(self):
        self.inputs.new("an_VectorSocket", "A")
        self.inputs.new("an_VectorSocket", "B")
        self.outputs.new("an_VectorSocket", "Result")

    def draw(self, layout):
        layout.prop(self, "operation")

    def getExecutionCode(self):
        op = self.operation
        if op == "ADD": return "$result$ = %a% + %b%"
        elif op == "SUBTRACT": return "$result$ = %a% - %b%"
        elif op == "MULTIPLY": return "$result$ = mathutils.Vector((%a%[0] * %b%[0], %a%[1] * %b%[1], %a%[2] * %b%[2]))"
        elif op == "CROSS": return "$result$ = %a%.cross(%b%)"
        elif op == "DIVIDE": return ("$result$ = mathutils.Vector((0, 0, 0)) \n"
                                     "if %b%[0] != 0: $result$[0] = %a%[0] / %b%[0] \n"
                                     "if %b%[1] != 0: $result$[1] = %a%[1] / %b%[1] \n"
                                     "if %b%[2] != 0: $result$[2] = %a%[2] / %b%[2]")
                                     
    def getModuleList(self):
        return ["mathutils"]
