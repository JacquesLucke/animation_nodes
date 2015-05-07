import bpy
from bpy.types import Node
from ... mn_node_base import AnimationNode
from ... mn_execution import nodePropertyChanged, allowCompiling, forbidCompiling
from ... mn_utils import *

class mn_ObjectInputNode(Node, AnimationNode):
    bl_idname = "mn_ObjectInputNode"
    bl_label = "Object Input"
    
    objectName = bpy.props.StringProperty(update = nodePropertyChanged)
    
    def init(self, context):
        forbidCompiling()
        self.inputs.new("mn_ObjectSocket", "Object").showName = False
        self.outputs.new("mn_ObjectSocket", "Object")
        allowCompiling()
        
    def getInputSocketNames(self):
        return {"Object" : "object"}
    def getOutputSocketNames(self):
        return {"Object" : "object"}
        
    def execute(self, object):
        return object
