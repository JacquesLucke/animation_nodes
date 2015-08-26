import bpy
from ... base_types.node import AnimationNode
from ... data_structures.splines.operations import connectSplines

class ConnectSplinesNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_ConnectSplinesNode"
    bl_label = "Connect Splines"

    def create(self):
        self.inputs.new("an_SplineListSocket", "Splines", "splines").showName = False
        self.outputs.new("an_SplineSocket", "Spline", "spline")

    def execute(self, splines):
        return connectSplines(splines)
