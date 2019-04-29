import bpy
from ... base_types import AnimationNode, VectorizedSocket

class CollectionOperationsNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_CollectionOperationsNode"
    bl_label = "Collection Operations"

    useObjectList: VectorizedSocket.newProperty()

    def create(self):
        self.newInput("Collection", "Collection", "collection", defaultDrawType = "PROPERTY_ONLY")
        self.newInput(VectorizedSocket("Object", "useObjectList",
            ("Object", "object"),
            ("Objects", "objects")))
            
        self.newInput("Boolean", "Linked", "linked")
        self.newOutput("Collection", "Collection", "collection")

    def execute(self, collection, objects, linked):
        if collection is None: return collection
        if objects is None: return collection
        
        if not self.useObjectList: objects = [objects]

        for object in objects:
            if object is None: continue
            if object.name in collection.objects:
                if not linked: collection.objects.unlink(object)
            else:
                if linked: collection.objects.link(object)

        return collection
    
