import bpy
from bpy.types import Node
from mathutils import *
from ... mn_node_base import AnimationNode
from ... mn_execution import nodePropertyChanged, nodeTreeChanged, allowCompiling, forbidCompiling

operationItems = [("MULTIPLY", "Multiply", "")]

class mn_MatrixMath(bpy.types.Node, AnimationNode):
    bl_idname = "mn_MatrixMath"
    bl_label = "Matrix Math"
    isDetermined = True
    
    operation = bpy.props.EnumProperty(items = operationItems, update = nodeTreeChanged)
    
    def init(self, context):
        forbidCompiling()
        self.inputs.new("mn_MatrixSocket", "A")
        self.inputs.new("mn_MatrixSocket", "B")
        self.outputs.new("mn_MatrixSocket", "Result")
        allowCompiling()
        
    def draw_buttons(self, context, layout):
        layout.prop(self, "operation")
        
    def getInputSocketNames(self):
        return {"A" : "a",
                "B" : "b"}
    def getOutputSocketNames(self):
        return {"Result" : "result"}

    def useInLineExecution(self):
        return True
    def getInLineExecutionString(self, outputUse):
        if self.operation == "MULTIPLY":
            return "$result$ = %a% * %b%"
