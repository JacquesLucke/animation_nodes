import bpy
from ... mn_node_base import AnimationNode
from ... mn_execution import nodePropertyChanged, allowCompiling, forbidCompiling

class mn_StringInputNode(bpy.types.Node, AnimationNode):
    bl_idname = "mn_StringInputNode"
    bl_label = "Text Input"
    
    def init(self, context):
        forbidCompiling()
        self.inputs.new("mn_StringSocket", "Text").showName = False
        self.outputs.new("mn_StringSocket", "Text")
        allowCompiling()
        
    def getInputSocketNames(self):
        return {"Text" : "text"}
    def getOutputSocketNames(self):
        return {"Text" : "text"}
        
    def execute(self, text):
        return text
