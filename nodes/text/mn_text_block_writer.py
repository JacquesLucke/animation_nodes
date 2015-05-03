import bpy
from bpy.types import Node
from animation_nodes.mn_node_base import AnimationNode
from animation_nodes.mn_execution import nodeTreeChanged, allowCompiling, forbidCompiling
from animation_nodes.mn_utils import *


class mn_TextBlockWriter(Node, AnimationNode):
    bl_idname = "mn_TextBlockWriter"
    bl_label = "Text Block Writer"
    
    def init(self, context):
        forbidCompiling()
        self.inputs.new("mn_TextBlockSocket", "Text Block").showName = False
        self.inputs.new("mn_StringSocket", "Text")
        self.outputs.new("mn_TextBlockSocket", "Text Block")
        allowCompiling()
        
    def getInputSocketNames(self):
        return {"Text Block" : "textBlock",
                "Text" : "text"}
    def getOutputSocketNames(self):
        return {"Text Block" : "textBlock"}

    def execute(self, textBlock, text):
        if textBlock is not None:
            textBlock.from_string(text)
        return textBlock
        
