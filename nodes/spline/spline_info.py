import bpy
from ... base_types.node import AnimationNode

class SplineInfo(bpy.types.Node, AnimationNode):
    bl_idname = "mn_SplineInfo"
    bl_label = "Spline Info"

    inputNames = { "Spline" : "spline" }

    outputNames = { "Points" : "points",
                    "Cyclic" : "cyclic" }

    def create(self):
        self.inputs.new("mn_SplineSocket", "Spline").showName = False
        self.outputs.new("mn_VectorListSocket", "Points")
        self.outputs.new("mn_BooleanSocket", "Cyclic")

    def execute(self, spline):
        spline.update()
        return spline.getPoints(), spline.isCyclic
