import bpy
from bpy.types import Node
from ... mn_node_base import AnimationNode
from ... mn_execution import nodePropertyChanged, allowCompiling, forbidCompiling

class mn_FloatInputNode(bpy.types.Node, AnimationNode):
    bl_idname = "mn_FloatInputNode"
    bl_label = "Float Input"
    isDetermined = True
    
    def init(self, context):
        forbidCompiling()
        self.inputs.new("mn_FloatSocket", "Number").showName = False
        self.outputs.new("mn_FloatSocket", "Number")
        allowCompiling()
        
    def getInputSocketNames(self):
        return {"Number" : "number"}
    def getOutputSocketNames(self):
        return {"Number" : "number"}
        
    def execute(self, number):
        return number

