import bpy
from bpy.types import Node
from bpy.props import *
from ... mn_node_base import AnimationNode
from ... mn_execution import nodePropertyChanged, allowCompiling, forbidCompiling
from ... data_structures.curve import *
from ... algorithms.mesh_generation.from_splines import revolveProfileAroundAxis

modeItems = [
    ("PARAMETER", "Same Parameter", ""),
    ("PROJECT", "Project Profile", "") ]

class mn_RevolveBezierSplines(Node, AnimationNode):
    bl_idname = "mn_RevolveBezierSplines"
    bl_label = "Revolve Bezier Splines"
    
    mode = EnumProperty(name = "Mode", items = modeItems, default = "PROJECT", update = nodePropertyChanged)
    
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
        
    def draw_buttons(self, context, layout):
        layout.prop(self, "mode")

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
            return revolveProfileAroundAxis(axis, profile, splineSamples, surfaceSamples, type = self.mode)
        else:
            return [], []