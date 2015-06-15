import bpy
from bpy.types import Node
from bpy.props import *
from ... mn_node_base import AnimationNode
from ... mn_execution import nodePropertyChanged, nodeTreeChanged, allowCompiling, forbidCompiling
from ... id_keys import getIDKeyData, getIDKeys
from ... utils.math import *


class mn_ObjectIDKey(Node, AnimationNode):
    bl_idname = "mn_ObjectIDKey"
    bl_label = "Object ID Key"
    outputUseParameterName = "useOutput"
    
    def selected_key_changed(self, context):
        self.key_name, self.key_type = self.selected_key.split("|")
        self.buildOutputSockets()
        nodeTreeChanged()
        
    def getIDKeyItems(self, context):
        return [(name + "|" + type, name, type) for name, type in getIDKeys()]
    
    selected_key = EnumProperty(items = getIDKeyItems, name = "ID Key", update = selected_key_changed)
    key_name = StringProperty()
    key_type = StringProperty()
    
    def init(self, context):
        forbidCompiling()
        self.inputs.new("mn_ObjectSocket", "Object").showName = False
        self.selected_key_changed(context)
        allowCompiling()
        
    def draw_buttons(self, context, layout):
        layout.prop(self, "selected_key", text = "")
        
    def buildOutputSockets(self):
        self.outputs.clear()
        forbidCompiling()
        if self.key_type == "Transforms":
            self.outputs.new("mn_VectorSocket", "Location")
            self.outputs.new("mn_VectorSocket", "Rotation")
            self.outputs.new("mn_VectorSocket", "Scale")
        if self.key_type == "Float":
            self.outputs.new("mn_FloatSocket", "Float")
        if self.key_type == "Integer":
            self.outputs.new("mn_IntegerSocket", "Integer")
        if self.key_type == "String":
            self.outputs.new("mn_StringSocket", "String")
        allowCompiling()
        
    def getInputSocketNames(self):
        return {"Object" : "object"}
    def getOutputSocketNames(self):
        return { socket.identifier : socket.identifier for socket in self.outputs }
        
    def execute(self, useOutput, object):
        data = getIDKeyData(object, self.key_name, self.key_type)
        
        if self.key_type in ("Float", "Integer", "String"): return data
        if self.key_type == "Transforms": return data[0], data[1], data[2]
