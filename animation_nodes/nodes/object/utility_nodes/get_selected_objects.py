import bpy
from .... events import isRendering
from .... base_types import AnimationNode
from .... utils.depsgraph import getActiveDepsgraph
from .... utils.selection import getSelectedObjects, getActiveObject

class GetSelectedObjectsNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_GetSelectedObjectsNode"
    bl_label = "Get Selected Objects"
    searchTags = ["Get Active Object"]

    def create(self):
        self.newOutput("Object List", "Selected Objects", "selectedObjects")
        self.newOutput("Object", "Active Object", "activeObject")

    def execute(self):
        if isRendering():
            return [], None
        else:
            viewLayer = getActiveDepsgraph().view_layer
            return getSelectedObjects(viewLayer), getActiveObject(viewLayer)

    def draw(self, layout):
        layout.label(text = "Disabled During Rendering", icon = "INFO")
