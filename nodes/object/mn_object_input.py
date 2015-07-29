import bpy
from ... base_types.node import AnimationNode
from ... mn_execution import nodePropertyChanged, allowCompiling, forbidCompiling
from ... mn_utils import *

class mn_ObjectInputNode(bpy.types.Node, AnimationNode):
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
