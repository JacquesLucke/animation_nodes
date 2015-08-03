import bpy
from bpy.props import *
from ... events import propertyChanged
from ... base_types.node import AnimationNode
from ... id_keys import getIDKeyInfo, getIDKeyItems


class ObjectIDKey(bpy.types.Node, AnimationNode):
    bl_idname = "an_ObjectIDKey"
    bl_label = "Object ID Key"

    inputNames = { "Object" : "object" }

    @property
    def outputNames(self):
        return { socket.identifier : socket.identifier for socket in self.outputs }

    def selectedKeyChanged(self, context):
        self.isKeySelected = self.selectedKey != "NONE"

        rebuild = True
        if self.isKeySelected:
            name, type = self.selectedKey.split("|")
            rebuild = self.keyName != name or self.keyType != type
            self.keyName, self.keyType = name, type

        if rebuild:
            self.buildOutputSockets()

    selectedKey = EnumProperty(items = getIDKeyItems, name = "ID Key", update = selectedKeyChanged)
    isKeySelected = BoolProperty(default = False)
    keyName = StringProperty()
    keyType = StringProperty()

    def create(self):
        self.inputs.new("an_ObjectSocket", "Object").showName = False
        self.selectedKeyChanged(context)

    def draw_buttons(self, context, layout):
        layout.prop(self, "selectedKey", text = "")

    def buildOutputSockets(self):
        self.outputs.clear()
        if self.isKeySelected:
            self.outputs.new("an_BooleanSocket", "Exists")
            if self.keyType == "Transforms":
                self.outputs.new("an_VectorSocket", "Location")
                self.outputs.new("an_VectorSocket", "Rotation")
                self.outputs.new("an_VectorSocket", "Scale")
            if self.keyType == "Float":
                self.outputs.new("an_FloatSocket", "Float")
            if self.keyType == "Integer":
                self.outputs.new("an_IntegerSocket", "Integer")
            if self.keyType == "String":
                self.outputs.new("an_StringSocket", "String")

    def execute(self, object):
        if not self.isKeySelected: return

        data, hasKey = getIDKeyInfo(object, self.keyName, self.keyType)

        if self.keyType in ("Float", "Integer", "String"): return hasKey, data
        if self.keyType == "Transforms": return hasKey, data[0], data[1], data[2]
