import bpy
from ... base_types.node import AnimationNode

class MakeObjectSmoothNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_MakeObjectSmoothNode"
    bl_label = "Make Object Smooth"

    def create(self):
        self.inputs.new("an_ObjectSocket", "Object", "object").defaultDrawType = "PROPERTY_ONLY"
        self.inputs.new("an_BooleanSocket", "Smooth", "smooth")
        self.outputs.new("an_ObjectSocket", "Object", "object")

    def execute(self, object, smooth):
        if getattr(object, "type", "") == "MESH":
            mesh = object.data
            smoothList = [smooth] * len(mesh.polygons)
            mesh.polygons.foreach_set("use_smooth", smoothList)
            mesh.update()
        return object
