import bpy
from ... events import propertyChanged
from ... base_types.node import AnimationNode

class ObjectGroupInput(bpy.types.Node, AnimationNode):
    bl_idname = "mn_ObjectGroupInput"
    bl_label = "Object Group Input"

    inputNames = { "Group" : "group" }
    outputNames = { "Objects" : "objects" }

    groupName = bpy.props.StringProperty(default = "", update = propertyChanged)

    def create(self):
        self.inputs.new("mn_ObjectGroupSocket", "Group").showName = False
        self.outputs.new("mn_ObjectListSocket", "Objects")

    def execute(self, group):
        return getattr(group, "objects", [])
