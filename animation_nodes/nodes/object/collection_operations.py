import bpy
from ... base_types import AnimationNode, VectorizedSocket

class CollectionOperationsNode(bpy.types.Node, AnimationNode):
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

    def getExecutionFunctionName(self):
        if self.useObjectList:
            return "executeMultipleObject"
        else:
            return "executeSingleObject"

    def executeMultipleObject(self, collection, objects, linked):
        if collection is None: return collection
        if objects is None: return collection
        
        for object in objects:
            if object is None: continue
            self.applyObject(collection, object, linked)

        return collection

    def executeSingleObject(self, collection, object, linked):
        if collection is None: return collection
        if object is None: return collection
        
        self.applyObject(collection, object, linked)

        return collection

    def applyObject(self, collection, object, linked):
        if object.name in collection.objects:
            if not linked: collection.objects.unlink(object)
        else:
            if linked: collection.objects.link(object)
    