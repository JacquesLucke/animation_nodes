import bpy
import math
from bpy.props import *
from ... base_types.node import AnimationNode
from ... events import executionCodeChanged


operationItems = [
    ("ADD", "Add", ""),
    ("SUBTRACT", "Subtract", ""),
    ("MULITPLY", "Multiply", ""),
    ("DIVIDE", "Divide", ""),
    ("SINE", "Sine", ""),
    ("COSINE", "Cosine", ""),
    ("TANGENT", "Tangent", ""),
    ("ARCSINE", "Arcsine", ""),
    ("ARCCOSINE", "Arccosine", ""),
    ("ARCTANGENT", "Arctangent", ""),
    ("POWER", "Power", ""),
    ("LOGARITHM", "Logarithm", ""),
    ("MINIMUM", "Minimum", ""),
    ("MAXIMUM", "Maximum", ""),
    ("ROUND", "Round", ""),
    ("LESSTHAN", "Less Than", ""),
    ("GREATHERTHAN", "Greather Than", ""),
    ("MODULO", "Modulo", ""),
    ("ABSOLUTE", "Absolute", ""),
    ("FLOOR", "Floor", ""),
    ("CEILING", "Ceiling", "")]

singleInputOperations = ("SINE", "COSINE", "TANGENT", "ARCSINE",
    "ARCCOSINE", "ARCTANGENT", "ABSOLUTE", "FLOOR", "CEILING")


class FloatMathNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_FloatMathNode"
    bl_label = "Math"
    isDetermined = True

    inputNames = { "A" : "a",
                   "B" : "b" }

    outputNames = { "Result" : "result" }

    def operationChanged(node, context):
        node.inputs[1].hide = node.operation in singleInputOperations
        executionCodeChanged()

    operation = EnumProperty(
        name = "Operation",
        default = "MULITPLY",
        items = operationItems,
        update = operationChanged)

    def create(self):
        self.inputs.new("an_FloatSocket", "A")
        self.inputs.new("an_FloatSocket", "B").value = 1.0
        self.outputs.new("an_FloatSocket", "Result")

    def draw_buttons(self, context, layout):
        layout.prop(self, "operation")

    def getNextNodeSuggestions(self):
        return [("an_FloatMathNode", (0, 0)),
                ("an_CombineVector", (0, 0)),
                ("an_FloatClamp", (0, 0))]

    def getExecutionCode(self):
        op = self.operation
        if op == "ADD": return "$result$ = %a% + %b%"
        elif op == "SUBTRACT": return "$result$ = %a% - %b%"
        elif op == "MULITPLY": return "$result$ = %a% * %b%"
        elif op == "DIVIDE": return ("if %b% == 0: $result$ = 0 \n"
                                     "else: $result$ = %a% / %b%")
        elif op == "SINE": return "$result$ = math.sin(%a%)"
        elif op == "COSINE": return "$result$ = math.cos(%a%)"
        elif op == "TANGENT": return "$result$ = math.tan(%a%)"
        elif op == "ARCSINE": return "$result$ = math.asin(min(max(%a%, -1), 1))"
        elif op == "ARCCOSINE": return "$result$ = math.acos(min(max(%a%, -1), 1))"
        elif op == "ARCTANGENT": return "$result$ = math.atan(%a%)"
        elif op == "POWER": return "$result$ = math.pow(%a%, %b%)"
        elif op == "LOGARITHM": return ("if %b% <= 0 or %b% == 1: $result$ = math.log(%a%) \n"
                                        "else: $result$ = math.log(%a%, %b%)")
        elif op == "MINIMUM": return "$result$ = min(%a%, %b%)"
        elif op == "MAXIMUM": return "$result$ = max(%a%, %b%)"
        elif op == "ROUND": return "$result$ = round(%a%, int(%b%))"
        elif op == "LESSTHAN": return "$result$ = %a% < %b%"
        elif op == "GREATHERTHAN": return "$result$ = %a% > %b%"
        elif op == "ABSOLUTE": return "$result$ = abs(%a%)"
        elif op == "MODULO": return ("if %b% == 0: $result$ = 0 \n"
                                     "else: $result$ = %a% % %b%")
        elif op == "FLOOR": return "$result$ = math.floor(%a%)"
        elif op == "CEILING": return "$result$ = math.ceil(%a%)"

    def getModuleList(self):
        return ["math"]
