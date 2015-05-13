import bpy
from bpy.types import Node
from ... mn_node_base import AnimationNode
from ... mn_execution import nodePropertyChanged, nodeTreeChanged, allowCompiling, forbidCompiling
from ... mn_utils import *

class mn_ObjectAttributeOutputNode(Node, AnimationNode):
    bl_idname = "mn_ObjectAttributeOutputNode"
    bl_label = "Object Attribute Output"
    
    def init(self, context):
        forbidCompiling()
        self.width = 200
        self.inputs.new("mn_ObjectSocket", "Object").showName = False
        self.inputs.new("mn_StringSocket", "Attribute").string = ""
        self.inputs.new("mn_GenericSocket", "Value")
        self.outputs.new("mn_ObjectSocket", "Object")
        allowCompiling()
        
    def getInputSocketNames(self):
        return {"Object" : "object",
                "Attribute" : "attribute",
                "Value" : "value"}
    def getOutputSocketNames(self):
        return {"Object" : "object"}
        
    def execute(self, object, attribute, value):
        try:
            if attribute.startswith("["):
                exec("object" + attribute + "=" + "value")
            else:
                exec("object." + attribute + "=" + "value")
        except:
            pass
        return object
