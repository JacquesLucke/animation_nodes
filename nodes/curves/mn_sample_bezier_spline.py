import bpy
from bpy.types import Node
from bpy.props import *
from ... mn_node_base import AnimationNode
from ... mn_execution import nodePropertyChanged, allowCompiling, forbidCompiling
from ... data_structures.curve import *


class mn_SampleBezierSpline(Node, AnimationNode):
    bl_idname = "mn_SampleBezierSpline"
    bl_label = "Sample Bezier Spline"
    
    def init(self, context):
        forbidCompiling()
        self.inputs.new("mn_BezierSplineSocket", "Spline").showName = False
        self.inputs.new("mn_IntegerSocket", "Amount").setMinMax(0, 10000000)
        self.outputs.new("mn_VectorListSocket", "Locations")
        allowCompiling()

    def getInputSocketNames(self):
        return {"Spline" : "spline",
                "Amount" : "amount"}

    def getOutputSocketNames(self):
        return {"Locations" : "locations"}

    def execute(self, spline, amount):
        spline.updateSegments()
        if spline.hasSegments:
            return spline.getSamples(max(amount, 0))
        else:
            return []