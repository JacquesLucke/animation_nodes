import bpy
from bpy.types import Node
from bpy.props import *
from ... mn_node_base import AnimationNode
from ... mn_execution import nodePropertyChanged, allowCompiling, forbidCompiling
from ... data_structures.curve import *
from ... algorithms.mesh_generation.from_splines import loftSplines

interpolationTypeItems = [
    ("LINEAR", "Linear", ""),
    ("BEZIER", "Bezier", "")]

class mn_LoftBezierSplines(Node, AnimationNode):
    bl_idname = "mn_LoftBezierSplines"
    bl_label = "Loft Bezier Splines"
    
    def settingsChanged(self, context):
        self.inputs["Smoothness"].hide = self.interpolationType != "BEZIER"
        self.inputs["Distribution"].hide = self.interpolationType != "LINEAR"
        nodePropertyChanged(self, context)
    
    interpolationType = EnumProperty(name = "Interpolation Type", default = "BEZIER", items = interpolationTypeItems, update = settingsChanged)
    
    def init(self, context):
        forbidCompiling()
        self.inputs.new("mn_BezierSplineListSocket", "Splines").showName = False
        socket = self.inputs.new("mn_IntegerSocket", "Spline Samples")
        socket.number = 16
        socket.setMinMax(2, 100000)
        socket = self.inputs.new("mn_IntegerSocket", "Surface Samples")
        socket.number = 16
        socket.setMinMax(2, 100000)
        socket = self.inputs.new("mn_BooleanSocket", "Cyclic").value = False
        socket = self.inputs.new("mn_FloatSocket", "Smoothness").number = 1
        socket = self.inputs.new("mn_InterpolationSocket", "Distribution")
        self.outputs.new("mn_VectorListSocket", "Vertices")
        self.outputs.new("mn_PolygonIndicesListSocket", "Polygons")
        self.settingsChanged(context)
        allowCompiling()
        
    def draw_buttons(self, context, layout):
        layout.prop(self, "interpolationType", text = "")

    def getInputSocketNames(self):
        return {"Splines" : "splines",
                "Spline Samples" : "splineSamples",
                "Surface Samples" : "surfaceSamples",
                "Cyclic" : "cyclic",
                "Smoothness" : "smoothness",
                "Distribution" : "distribution"}

    def getOutputSocketNames(self):
        return {"Vertices" : "vertices",
                "Polygons" : "polygons"}

    def execute(self, splines, splineSamples, surfaceSamples, cyclic, smoothness, distribution):
        def canExecute():
            if splineSamples < 2: return False
            if surfaceSamples < 2: return False
            if len(splines) < 2: return False
            for spline in splines:
                if not spline.hasSegments: return False
            return True
            
        for spline in splines:
            spline.updateSegments()
        
        if canExecute():
            return loftSplines(splines, 
                               splineSamples, surfaceSamples, 
                               self.interpolationType, cyclic, smoothness, distribution)
        else:
            return [], []