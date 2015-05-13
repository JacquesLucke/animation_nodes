import bpy
from bpy.types import Node
from ... mn_node_base import AnimationNode
from ... mn_execution import nodeTreeChanged, allowCompiling, forbidCompiling
import math

def updateNode(node, context):
    nodeTreeChanged()


class mn_VectorMathNode(Node, AnimationNode):
    bl_idname = "mn_VectorMathNode"
    bl_label = "Vector Math"
    isDetermined = True
    
    mathTypes = [
        ("ADD", "Add", ""),
        ("SUBTRACT", "Subtract", ""),
        ("MULTIPLY", "Multiply", "Multiply element by element"),
        ("DIVIDE", "Divide", "Divide element by element"),
        ("CROSS", "Cross Product", "Calculate the cross/vector product, yielding a vector that is orthogonal to both input vectors")]
    mathTypesProperty = bpy.props.EnumProperty(name="Operation", items=mathTypes, default="ADD", update=updateNode)
    
    def init(self, context):
        forbidCompiling()
        self.inputs.new("mn_VectorSocket", "A")
        self.inputs.new("mn_VectorSocket", "B")
        self.outputs.new("mn_VectorSocket", "Result")
        allowCompiling()
        
    def getInputSocketNames(self):
        return {"A" : "a", "B" : "b"}
    def getOutputSocketNames(self):
        return {"Result" : "result"}
        
    def draw_buttons(self, context, layout):
        layout.prop(self, "mathTypesProperty")
        
    def useInLineExecution(self):
        return True
    def getInLineExecutionString(self, outputUse):
        if outputUse["Result"]:
            op = self.mathTypesProperty
            if op == "ADD": return "$result$ = %a% + %b%"
            elif op == "SUBTRACT": return "$result$ = %a% - %b%"
            elif op == "MULTIPLY": return "$result$ = mathutils.Vector((%a%[0] * %b%[0], %a%[1] * %b%[1], %a%[2] * %b%[2]))"
            elif op == "DIVIDE": return '''
$result$ = mathutils.Vector((0, 0, 0))
if %b%[0] != 0: $result$[0] = %a%[0] / %b%[0]
if %b%[1] != 0: $result$[1] = %a%[1] / %b%[1]
if %b%[2] != 0: $result$[2] = %a%[2] / %b%[2]
'''
            elif op == "CROSS": return "$result$ = %a%.cross(%b%)"
        return ""
    def getModuleList(self):
        return ["mathutils"]

