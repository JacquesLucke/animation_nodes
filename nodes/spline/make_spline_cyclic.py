import bpy
from ... base_types.node import AnimationNode

class MakeSplineCyclic(bpy.types.Node, AnimationNode):
    bl_idname = "mn_MakeSplineCyclic"
    bl_label = "Make Spline Cyclic"

    inputNames = { "Spline" : "spline",
                   "Cyclic" : "cyclic" }

    outputNames = { "Spline" : "spline" }

    def create(self):
        self.inputs.new("mn_SplineSocket", "Spline").showName = False
        self.inputs.new("mn_BooleanSocket", "Cyclic").value = True
        self.outputs.new("mn_SplineSocket", "Spline")

    def execute(self, spline, cyclic):
        spline.isCyclic = cyclic
        spline.isChanged = True
        return spline
