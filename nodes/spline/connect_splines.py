import bpy
from ... base_types.node import AnimationNode
from ... data_structures.splines.operations import connectSplines

class ConnectSplines(bpy.types.Node, AnimationNode):
    bl_idname = "an_ConnectSplines"
    bl_label = "Connect Splines"

    inputNames = { "Splines" : "splines" }
    outputNames = { "Spline" : "spline" }

    def create(self):
        self.inputs.new("an_SplineListSocket", "Splines").showName = False
        self.outputs.new("an_SplineSocket", "Spline")

    def execute(self, splines):
        return connectSplines(splines)
