import bpy
from .... events import isRendering
from .... base_types.node import AnimationNode

class GetActiveCameraNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_GetActiveCameraNode"
    bl_label = "Get Active Camera"
    searchTags = ["Get Active Camera"]
    bl_width_default = 200

    def create(self):
       self.newOutput("Object", "Active Camera", "activeCamera")

    def execute(self):
        context = bpy.context
        return context.scene.camera
