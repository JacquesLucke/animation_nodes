import bpy
from ... mn_node_base import AnimationNode
from ... mn_execution import nodePropertyChanged, allowCompiling, forbidCompiling

class mn_ReplicateStringsNode(bpy.types.Node, AnimationNode):
    bl_idname = "mn_ReplicateStringsNode"
    bl_label = "Replicate Text"
    
    def init(self, context):
        forbidCompiling()
        self.inputs.new("mn_StringSocket", "Text")
        self.inputs.new("mn_IntegerSocket", "Amount")
        self.outputs.new("mn_StringSocket", "Text")
        allowCompiling()
        
    def execute(self, input):
        output = {}
        output["Text"] = input["Text"] * input["Amount"]
        return output
