import bpy
from ... base_types.node import AnimationNode

class SplineInfoNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_SplineInfoNode"
    bl_label = "Spline Info"

    def create(self):
        self.newInput("Spline", "Spline", "spline", defaultDrawType = "PROPERTY_ONLY")
        self.newOutput("Vector List", "Points", "points")
        self.newOutput("Boolean", "Cyclic", "cyclic")

    def execute(self, spline):
        raise NotImplementedError()
        spline.update()
        return spline.getPoints(), spline.isCyclic
