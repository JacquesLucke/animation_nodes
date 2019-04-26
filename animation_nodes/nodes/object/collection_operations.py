import bpy
from ... base_types import AnimationNode

class CollectionOperationsNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_CollectionOperationsNode"
    bl_label = "Collection Operations"

    def create(self):
        self.newInput("Collection", "Collection", "collection", defaultDrawType = "PROPERTY_ONLY")
        self.newInput("Object", "Object", "object", defaultDrawType = "PROPERTY_ONLY")
        self.newInput("Boolean", "Linked", "linked")
        self.newOutput("Collection", "Collection", "collection")

    def execute(self, collection, object, linked):
        if collection is None: return collection
        if object is None: return collection

        if object.name in collection.objects:
            if not linked: collection.objects.unlink(object)
        else:
            if linked: collection.objects.link(object)

        return collection
    
