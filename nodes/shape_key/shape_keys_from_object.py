import bpy
from ... base_types.node import AnimationNode

class ShapeKeysFromObjectNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_ShapeKeysFromObjectNode"
    bl_label = "Shape Keys from Object"

    def create(self):
        self.newInput("an_ObjectSocket", "Object", "object").defaultDrawType = "PROPERTY_ONLY"
        self.newOutput("an_ShapeKeyListSocket", "Shape Keys", "shapeKeys")
        self.newOutput("an_ShapeKeySocket", "Reference Key", "referenceKey")

    def execute(self, object):
        if object is None: return [], None
        if object.type not in ("MESH", "CURVE", "LATTICE"): return [], None
        if object.data.shape_keys is None: return [], None

        reference = object.data.shape_keys.reference_key
        return list(object.data.shape_keys.key_blocks), reference
