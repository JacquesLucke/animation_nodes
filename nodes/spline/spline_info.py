import bpy
from ... base_types.node import AnimationNode

class SplineInfo(bpy.types.Node, AnimationNode):
    bl_idname = "an_SplineInfo"
    bl_label = "Spline Info"

    inputNames = { "Spline" : "spline" }

    outputNames = { "Points" : "points",
                    "Cyclic" : "cyclic" }

    def create(self):
        self.inputs.new("an_SplineSocket", "Spline").showName = False
        self.outputs.new("an_VectorListSocket", "Points")
        self.outputs.new("an_BooleanSocket", "Cyclic")

    def execute(self, spline):
        spline.update()
        return spline.getPoints(), spline.isCyclic
