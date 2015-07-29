import bpy
from ... mn_node_base import AnimationNode
from ... mn_execution import nodeTreeChanged, allowCompiling, forbidCompiling
from ... mn_utils import *


class mn_TextBlockReader(bpy.types.Node, AnimationNode):
    bl_idname = "mn_TextBlockReader"
    bl_label = "Text Block Reader"
    outputUseParameterName = "useOutput"
    
    def init(self, context):
        forbidCompiling()
        self.inputs.new("mn_TextBlockSocket", "Text Block").showName = False
        self.outputs.new("mn_StringSocket", "Text")
        self.outputs.new("mn_StringListSocket", "Lines")
        allowCompiling()
        
    def getInputSocketNames(self):
        return {"Text Block" : "textBlock"}
    def getOutputSocketNames(self):
        return {"Text" : "text",
                "Lines" : "lines"}

    def execute(self, useOutput, textBlock):
        text = ""
        if textBlock is not None:
            text = textBlock.as_string()
            
        if useOutput["Lines"]: return text, text.split("\n")
        else: return text, []
        
