import bpy
from ... base_types.node import AnimationNode

class ObjectGroupInput(bpy.types.Node, AnimationNode):
    bl_idname = "an_ObjectGroupInput"
    bl_label = "Object Group Input"

    def create(self):
        self.inputs.new("an_ObjectGroupSocket", "Group", "group").showName = False
        self.outputs.new("an_ObjectListSocket", "Objects", "objects")

    def execute(self, group):
        return list(getattr(group, "objects", []))
