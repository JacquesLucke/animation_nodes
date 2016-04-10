import bpy
from ... base_types.node import AnimationNode

class SplineInfoNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_SplineInfoNode"
    bl_label = "Spline Info"

    def create(self):
        self.newInput("an_SplineSocket", "Spline", "spline").defaultDrawType = "PROPERTY_ONLY"
        self.newOutput("an_VectorListSocket", "Points", "points")
        self.newOutput("an_BooleanSocket", "Cyclic", "cyclic")

    def execute(self, spline):
        spline.update()
        return spline.getPoints(), spline.isCyclic
