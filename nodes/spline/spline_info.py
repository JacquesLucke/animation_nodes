import bpy
from ... base_types.node import AnimationNode

class SplineInfoNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_SplineInfoNode"
    bl_label = "Spline Info"

    def create(self):
        self.inputs.new("an_SplineSocket", "Spline", "spline").showName = False
        self.outputs.new("an_VectorListSocket", "Points", "points")
        self.outputs.new("an_BooleanSocket", "Cyclic", "cyclic")

    def execute(self, spline):
        spline.update()
        return spline.getPoints(), spline.isCyclic
