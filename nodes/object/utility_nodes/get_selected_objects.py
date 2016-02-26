import bpy
from .... events import isRendering
from .... base_types.node import AnimationNode

class GetSelectedObjectsNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_GetSelectedObjectsNode"
    bl_label = "Get Selected Objects"
    searchTags = ["Get Active Object"]

    def create(self):
        self.width = 200
        self.outputs.new("an_ObjectListSocket", "Selected Objects", "selectedObjects")
        self.outputs.new("an_ObjectSocket", "Active Object", "activeObject")

    def execute(self):
        if isRendering():
            return [], None
        else:
            context = bpy.context
            return context.selected_objects, context.active_object

    def draw(self, layout):
        layout.label("Disabled During Rendering", icon = "INFO")
