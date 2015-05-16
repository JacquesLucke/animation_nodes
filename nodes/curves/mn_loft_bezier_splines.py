import bpy
from bpy.types import Node
from ... mn_node_base import AnimationNode
from ... mn_execution import nodePropertyChanged, allowCompiling, forbidCompiling
from ... data_structures.curve import *
from ... utils.curve_to_mesh import loftSplines

class mn_LoftBezierSplines(Node, AnimationNode):
    bl_idname = "mn_LoftBezierSplines"
    bl_label = "Loft Bezier Splines"
    
    def init(self, context):
        forbidCompiling()
        self.inputs.new("mn_BezierSplineSocket", "Spline 1").showName = False
        self.inputs.new("mn_BezierSplineSocket", "Spline 2").showName = False
        socket = self.inputs.new("mn_IntegerSocket", "Spline Samples")
        socket.number = 16
        socket.setMinMax(2, 100000)
        socket = self.inputs.new("mn_IntegerSocket", "Surface Samples")
        socket.number = 16
        socket.setMinMax(2, 100000)
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
        spline1.updateSegments()
        spline2.updateSegments()
        
        if spline1.hasSegments and spline2.hasSegments and splineSamples >= 2 and surfaceSamples >= 2:
            return loftSplines(spline1, spline2, splineSamples, surfaceSamples)
        else:
            return [], []