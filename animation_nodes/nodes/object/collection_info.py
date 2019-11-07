import bpy
from ... base_types import AnimationNode

class CollectionInfoNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_CollectionInfoNode"
    bl_label = "Collection Info"

    def create(self):
        self.newInput("Collection", "Collection", "collection", defaultDrawType = "PROPERTY_ONLY")
        self.newOutput("Object List", "Objects", "objects")
        self.newOutput("Object List", "All Objects", "allObjects")
        self.newOutput("Collection List", "Children", "children")

    def execute(self, collection):
        objects = list(getattr(collection, "objects", []))
        allObjects = list(getattr(collection, "all_objects", []))
        children = list(getattr(collection, "children", []))
        return objects, allObjects, children
