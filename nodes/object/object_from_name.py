import bpy
from ... base_types.node import AnimationNode

class ObjectFromNameNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_ObjectFromNameNode"
    bl_label = "Object from Name"

    def create(self):
        self.inputs.new("an_StringSocket", "Name", "name").defaultDrawType = "PROPERTY_ONLY"
        self.outputs.new("an_ObjectSocket", "Object", "object")

    def getExecutionCode(self):
        return "object = bpy.data.objects.get(name)"
