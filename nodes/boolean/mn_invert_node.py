import bpy
from bpy.types import Node
from ... mn_node_base import AnimationNode
from ... mn_execution import nodePropertyChanged, nodeTreeChanged, allowCompiling, forbidCompiling


class mn_InvertNode(Node, AnimationNode):
    bl_idname = "mn_InvertNode"
    bl_label = "Invert Boolean"
    
    def init(self, context):
        forbidCompiling()
        self.inputs.new("mn_BooleanSocket", "Input")
        self.outputs.new("mn_BooleanSocket", "Output")
        allowCompiling()
        
    def getInputSocketNames(self):
        return {"Input" : "input"}
    def getOutputSocketNames(self):
        return {"Output" : "output"}
        
    def useInLineExecution(self):
        return True
    def getInLineExecutionString(self, outputUse):
        return "$output$ = not %input%"
