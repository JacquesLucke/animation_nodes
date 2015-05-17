import bpy
from bpy.types import Node
from ... mn_node_base import AnimationNode
from ... mn_execution import nodePropertyChanged, allowCompiling, forbidCompiling
from ... data_structures.curve import *
from ... utils.curve_to_mesh import generateLoftedSurface

class mn_LoftBezierSplines(Node, AnimationNode):
    bl_idname = "mn_LoftBezierSplines"
    bl_label = "Loft Bezier Splines"
    
    def init(self, context):
        forbidCompiling()
        self.inputs.new("mn_BezierSplineListSocket", "Splines").showName = False
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
        return {"Splines" : "splines",
                "Spline Samples" : "splineSamples",
                "Surface Samples" : "surfaceSamples"}

    def getOutputSocketNames(self):
        return {"Vertices" : "vertices",
                "Polygons" : "polygons"}

    def execute(self, splines, splineSamples, surfaceSamples):
        for spline in splines:
            spline.updateSegments()
        
        if len(splines) >= 2 and splineSamples >= 2 and surfaceSamples >= 2:
            return generateLoftedSurface(splines, splineSamples, surfaceSamples)
        else:
            return [], []