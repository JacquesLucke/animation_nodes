import bpy
from bpy.types import Node
from bpy.props import *
from ... mn_node_base import AnimationNode
from ... mn_execution import nodePropertyChanged, nodeTreeChanged, allowCompiling, forbidCompiling
from ... id_keys import getIDKeyData, getIDKeys


class mn_ObjectIDKey(Node, AnimationNode):
    bl_idname = "mn_ObjectIDKey"
    bl_label = "Object ID Key"
    
    def selected_key_changed(self, context):
        self.isKeySelected = self.selected_key != "NONE"
        if self.isKeySelected:
            self.keyName, self.keyType = self.selected_key.split("|")
        self.buildOutputSockets()
        nodeTreeChanged()
        
    def getIDKeyItems(self, context):
        items = []
        for item in getIDKeys():
            name, type = item.name, item.type
            items.append((name + "|" + type, name, type))
        if len(items) == 0:
            items.append(("NONE", "No ID Key", ""))
        return items
    
    selected_key = EnumProperty(items = getIDKeyItems, name = "ID Key", update = selected_key_changed)
    keyName = StringProperty()
    keyType = StringProperty()
    isKeySelected = BoolProperty(default = False)
    
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
        if self.keyType == "Transforms":
            self.outputs.new("mn_VectorSocket", "Location")
            self.outputs.new("mn_VectorSocket", "Rotation")
            self.outputs.new("mn_VectorSocket", "Scale")
        if self.keyType == "Float":
            self.outputs.new("mn_FloatSocket", "Float")
        if self.keyType == "Integer":
            self.outputs.new("mn_IntegerSocket", "Integer")
        if self.keyType == "String":
            self.outputs.new("mn_StringSocket", "String")
        allowCompiling()
        
    def getInputSocketNames(self):
        return {"Object" : "object"}
    def getOutputSocketNames(self):
        return { socket.identifier : socket.identifier for socket in self.outputs }
        
    def execute(self, object):
        if not self.isKeySelected: return
        
        data = getIDKeyData(object, self.keyName, self.keyType)
        
        if self.keyType in ("Float", "Integer", "String"): return data
        if self.keyType == "Transforms": return data[0], data[1], data[2]
