import bpy
from ... base_types.node import AnimationNode

class MakeSplineCyclic(bpy.types.Node, AnimationNode):
    bl_idname = "an_MakeSplineCyclic"
    bl_label = "Make Spline Cyclic"

    def create(self):
        socket = self.inputs.new("an_SplineSocket", "Spline", "spline")
        socket.dataIsModified = True
        socket.showName = False
        self.inputs.new("an_BooleanSocket", "Cyclic", "cylic").value = True
        self.outputs.new("an_SplineSocket", "Spline", "outSpline")

    def execute(self, spline, cyclic):
        spline.isCyclic = cyclic
        spline.isChanged = True
        return spline
