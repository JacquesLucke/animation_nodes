import bpy
from bpy.types import Node
from ... mn_node_base import AnimationNode
from ... mn_execution import nodePropertyChanged, allowCompiling, forbidCompiling
from ... data_structures.curve import *

class mn_LoftBezierSplines(Node, AnimationNode):
    bl_idname = "mn_LoftBezierSplines"
    bl_label = "Loft Bezier Splines"
    
    def init(self, context):
        forbidCompiling()
        self.inputs.new("mn_BezierSplineSocket", "Spline 1").showName = False
        self.inputs.new("mn_BezierSplineSocket", "Spline 2").showName = False
        self.inputs.new("mn_IntegerSocket", "Spline Samples").number = 16
        self.inputs.new("mn_FloatSocket", "Surface Samples").number = 16
        self.outputs.new("mn_VectorListSocket", "Vertices")
        self.outputs.new("mn_PolygonIndicesListSocket", "Polygons")
        allowCompiling()

    def getInputSocketNames(self):
        return {"Spline 1" : "spline1",
                "Spline 2" : "spline2",
                "Spline Samples" : "splineSamples",
                "Surface Samples" : "surfaceSamples"}

    def getOutputSocketNames(self):
        return {"Vertices" : "vertices",
                "Polygons" : "polygons"}

    def execute(self, spline1, spline2, splineSamples, surfaceSamples):
        spline.updateSegments()
        return loftSplines(spline1, spline2, splineSamples, surfaceSamples)

        
def loftSplines(spline1, spline2, splineSamples, surfaceSamples):
    sampledPoints1 = spline1.getSamples(splineSamples)
    sampledPoints2 = spline2.getSamples(splineSamples)