import bpy
from ... base_types.node import AnimationNode

class MakeObjectSmooth(bpy.types.Node, AnimationNode):
    bl_idname = "an_MakeObjectSmooth"
    bl_label = "Make Object Smooth"

    inputNames = { "Object" : "object",
                   "Smooth" : "smooth" }

    outputNames = { "Object" : "object" }

    def create(self):
        self.inputs.new("an_ObjectSocket", "Object").showName = False
        self.inputs.new("an_BooleanSocket", "Smooth")
        self.outputs.new("an_ObjectSocket", "Object")

    def execute(self, object, smooth):
        if getattr(object, "type", "") == "MESH":
            for polygon in object.data.polygons:
                polygon.use_smooth = smooth
        return object
