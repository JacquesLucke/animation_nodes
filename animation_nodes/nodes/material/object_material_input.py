import bpy
from ... base_types import AnimationNode

class ObjectMaterialInputNode(AnimationNode, bpy.types.Node):
    bl_idname = "an_ObjectMaterialInputNode"
    bl_label = "Object Material Input"

    def create(self):
        self.newInput("Object", "Object", "object", defaultDrawType = "PROPERTY_ONLY")
        self.newOutput("Material List", "Materials", "materials")

    def execute(self, object):
        if object is None or not hasattr(object.data, "materials"): return []
        return [material for material in object.data.materials if material]

