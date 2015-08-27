import bpy
from ... base_types.node import AnimationNode

class CreateObjectNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_CreateObjectNode"
    bl_label = "Create Object"
    options = {"No Auto Execution"}

    def create(self):
        self.inputs.new("an_StringSocket", "Name", "name")
        self.outputs.new("an_ObjectSocket", "Object", "object")

    def execute(self, name):
        object = bpy.data.objects.new(name, None)
        bpy.context.scene.objects.link(object)
        return object
