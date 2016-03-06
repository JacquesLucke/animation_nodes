import bpy
from ... base_types.node import AnimationNode

class GetObjectsFromGroupNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_GetObjectsFromGroupNode"
    bl_label = "Objects from Group"

    def create(self):
        self.inputs.new("an_ObjectGroupSocket", "Group", "group").defaultDrawType = "PROPERTY_ONLY"
        self.outputs.new("an_ObjectListSocket", "Objects", "objects")

    def execute(self, group):
        return list(getattr(group, "objects", []))
