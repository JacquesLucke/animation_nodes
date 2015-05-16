import bpy
from bpy.types import Node
from ... mn_node_base import AnimationNode
from ... mn_execution import nodePropertyChanged, allowCompiling, forbidCompiling
from ... data_structures.curve import *
from ... utils.curve_to_mesh import generateRevolvedSurface_SameParameter

class mn_RevolveBezierSplines(Node, AnimationNode):
    bl_idname = "mn_RevolveBezierSplines"
    bl_label = "Revolve Bezier Splines"
    
    def init(self, context):
        forbidCompiling()
        self.inputs.new("mn_BezierSplineSocket", "Axis")
        self.inputs.new("mn_BezierSplineSocket", "Profile")
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
        return {"Axis" : "axis",
                "Profile" : "profile",
                "Spline Samples" : "splineSamples",
                "Surface Samples" : "surfaceSamples"}

    def getOutputSocketNames(self):
        return {"Vertices" : "vertices",
                "Polygons" : "polygons"}

    def execute(self, axis, profile, splineSamples, surfaceSamples):
        axis.updateSegments()
        profile.updateSegments()
        
        if axis.hasSegments and profile.hasSegments and splineSamples >= 2 and surfaceSamples >= 2:
            return generateRevolvedSurface_SameParameter(axis, profile, splineSamples, surfaceSamples)
        else:
            return [], []