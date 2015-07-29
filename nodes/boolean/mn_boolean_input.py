import bpy
from ... mn_node_base import AnimationNode
from ... mn_execution import nodePropertyChanged, allowCompiling, forbidCompiling

class mn_BooleanInputNode(bpy.types.Node, AnimationNode):
    bl_idname = "mn_BooleanInputNode"
    bl_label = "Boolean Input"
    isDetermined = True
    
    def init(self, context):
        forbidCompiling()
        self.inputs.new("mn_BooleanSocket", "Boolean")
        self.outputs.new("mn_BooleanSocket", "Boolean")
        allowCompiling()
        
    def getInputSocketNames(self):
        return {"Boolean" : "boolean"}
    def getOutputSocketNames(self):
        return {"Boolean" : "boolean"}
        
    def execute(self, boolean):
        return boolean
