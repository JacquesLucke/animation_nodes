import bpy
from bpy.types import Node
from bpy.props import *
from ... mn_node_base import AnimationNode
from ... mn_execution import nodePropertyChanged, nodeTreeChanged, allowCompiling, forbidCompiling
from ... id_keys import getIDKeyInfo, getIDKeyItems


class mn_ObjectIDKey(Node, AnimationNode):
    bl_idname = "mn_ObjectIDKey"
    bl_label = "Object ID Key"
    
    def selectedKey_changed(self, context):
        self.isKeySelected = self.selectedKey != "NONE"
        if self.isKeySelected:
            self.keyName, self.keyType = self.selectedKey.split("|")
        self.buildOutputSockets()
        nodeTreeChanged()
    
    selectedKey = EnumProperty(items = getIDKeyItems, name = "ID Key", update = selectedKey_changed)
    keyName = StringProperty()
    keyType = StringProperty()
    isKeySelected = BoolProperty(default = False)
    
    def init(self, context):
        forbidCompiling()
        self.inputs.new("mn_ObjectSocket", "Object").showName = False
        self.selectedKey_changed(context)
        allowCompiling()
        
    def draw_buttons(self, context, layout):
        layout.prop(self, "selectedKey", text = "")
        
    def buildOutputSockets(self):
        forbidCompiling()
        self.outputs.clear()
        if self.isKeySelected:
            self.outputs.new("mn_BooleanSocket", "Exists")
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
        
        data, hasKey = getIDKeyInfo(object, self.keyName, self.keyType)
        
        if self.keyType in ("Float", "Integer", "String"): return hasKey, data
        if self.keyType == "Transforms": return hasKey, data[0], data[1], data[2]
