import bpy

from bpy.types import Node
from ... mn_node_base import AnimationNode
from ... mn_execution import allowCompiling, forbidCompiling

defaultOperand1 = 1.0
defaultOperand2 = 2.0

class mn_MathNumberOperatorNode(Node, AnimationNode):
    bl_idname = "mn_MathNumberOperatorNode"
    bl_label = "Number Operator"

    operator_items = [ ("Add", "Add", "Returns Operand1 + Operand2"), 
                       ("Subtract", "Subtract", "Returns Operand1 - Operand2"), 
                       ("Multiply", "Multiply", "Returns Operand1 * Operand2"), 
                       ("Divide", "Divide", "Returns Operand1 / Operand2 -- or 0.0")]
    operator = bpy.props.EnumProperty(name = "Operator", items = operator_items, default = "Add")
        
    def draw_buttons(self, context, layout):
        layout.prop(self, "operator")

    def init(self, context):
        forbidCompiling()
        self.inputs.new("mn_FloatSocket", "Operand 1").number = defaultOperand1
        self.inputs.new("mn_FloatSocket", "Operand 2").number = defaultOperand2
        self.outputs.new("mn_FloatSocket", "Result")
        allowCompiling()

    def getInputSocketNames(self):
        return {"Operand 1" : "operand1",
                "Operand 2" : "operand2"}

    def getOutputSocketNames(self):
        return {"Result" : "result"}

    def execute(self, operand1, operand2):
        try:
            if self.operator == "Add": return operand1 + operand2
            if self.operator == "Subtract": return operand1 - operand2
            if self.operator == "Multiply": return operand1 * operand2
            if self.operator == "Divide": return operand1 / operand2
        except: return 0.0
