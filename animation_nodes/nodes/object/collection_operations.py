import bpy
from ... base_types import AnimationNode, VectorizedSocket

class CollectionOperationsNode(AnimationNode, bpy.types.Node):
    bl_idname = "an_CollectionOperationsNode"
    bl_label = "Collection Operations"
    codeEffects = [VectorizedSocket.CodeEffect]

    useObjectList: VectorizedSocket.newProperty()

    def create(self):
        self.newInput("Collection", "Collection", "collection", defaultDrawType = "PROPERTY_ONLY")
        self.newInput(VectorizedSocket("Object", "useObjectList",
            ("Object", "object", dict(defaultDrawType = "PROPERTY_ONLY")),
            ("Objects", "objects", dict(defaultDrawType = "PROPERTY_ONLY"))))
            
        self.newInput("Boolean", "Linked", "linked")
        self.newOutput("Collection", "Collection", "collection")

    def getExecutionCode(self, required):
        return "collection = self.executeSingleObject(collection, object, linked)"

    def executeSingleObject(self, collection, object, linked):
        if collection is None: return collection
        if object is None: return collection
        
        if object.name in collection.objects:
            if not linked: collection.objects.unlink(object)
        else:
            if linked: collection.objects.link(object)

        return collection
