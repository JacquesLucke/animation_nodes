import bpy
from bpy.types import Node
from ... mn_node_base import AnimationNode
from ... mn_execution import nodePropertyChanged, allowCompiling, forbidCompiling
from ... data_structures.curve import *
from ... utils.curve_to_mesh import generateLoftedSurface

interpolationTypeItems = [
    ("LINEAR", "Linear", ""),
    ("BEZIER", "Bezier", "")]

class mn_LoftBezierSplines(Node, AnimationNode):
    bl_idname = "mn_LoftBezierSplines"
    bl_label = "Loft Bezier Splines"
    
    def settingsChanged(self, context):
        self.inputs["Smoothness"].hide = self.interpolationType != "BEZIER"
        nodePropertyChanged(self, context)
    
    interpolationType = bpy.props.EnumProperty(name = "Interpolation Type", items = interpolationTypeItems, update = settingsChanged)
    
    def init(self, context):
        forbidCompiling()
        self.inputs.new("mn_BezierSplineListSocket", "Splines").showName = False
        socket = self.inputs.new("mn_IntegerSocket", "Spline Samples")
        socket.number = 16
        socket.setMinMax(2, 100000)
        socket = self.inputs.new("mn_IntegerSocket", "Surface Samples")
        socket.number = 16
        socket.setMinMax(2, 100000)
        socket = self.inputs.new("mn_FloatSocket", "Smoothness").number = 1
        self.outputs.new("mn_VectorListSocket", "Vertices")
        self.outputs.new("mn_PolygonIndicesListSocket", "Polygons")
        allowCompiling()
        
    def draw_buttons(self, context, layout):
        layout.prop(self, "interpolationType", text = "")

    def getInputSocketNames(self):
        return {"Splines" : "splines",
                "Spline Samples" : "splineSamples",
                "Surface Samples" : "surfaceSamples",
                "Smoothness" : "smoothness"}

    def getOutputSocketNames(self):
        return {"Vertices" : "vertices",
                "Polygons" : "polygons"}

    def execute(self, splines, splineSamples, surfaceSamples, smoothness):
        for spline in splines:
            spline.updateSegments()
        
        if len(splines) >= 2 and splineSamples >= 2 and surfaceSamples >= 2:
            return generateLoftedSurface(splines, splineSamples, surfaceSamples, type = self.interpolationType, smoothness = smoothness)
        else:
            return [], []