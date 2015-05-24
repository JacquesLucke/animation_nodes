import bpy
from bpy.types import Node
from bpy.props import *
from ... mn_node_base import AnimationNode
from ... mn_execution import nodePropertyChanged, allowCompiling, forbidCompiling
from ... algorithms.mesh_generation.from_splines import loftSplines

interpolationTypeItems = [
    ("LINEAR", "Linear", ""),
    ("BEZIER", "Bezier", "")]

class mn_LoftSplines(Node, AnimationNode):
    bl_idname = "mn_LoftSplines"
    bl_label = "Loft Splines"
    
    def settingChanged(self, context):
        self.inputs["Smoothness"].hide = self.interpolationType != "BEZIER"
        nodePropertyChanged(self, context)
        
    interpolationType = EnumProperty(name = "Interpolation Type", default = "BEZIER", items = interpolationTypeItems, update = settingChanged)
        
    def init(self, context):
        forbidCompiling()
        self.inputs.new("mn_SplineListSocket", "Splines")
        socket1 = self.inputs.new("mn_IntegerSocket", "Spline Samples")
        socket2 = self.inputs.new("mn_IntegerSocket", "Surface Samples")
        for socket in (socket1, socket2):
            socket.number = 16
            socket.setMinMax(2, 100000)
        self.inputs.new("mn_BooleanSocket", "Cyclic").value = False
        self.inputs.new("mn_FloatSocket", "Smoothness").number = 0.3333
        self.outputs.new("mn_VectorListSocket", "Vertices")
        self.outputs.new("mn_PolygonIndicesListSocket", "Polygons")
        self.width += 20
        self.settingChanged(context)
        allowCompiling()
        
    def draw_buttons(self, context, layout):
        layout.prop(self, "interpolationType", text = "")

    def getInputSocketNames(self):
        return {"Splines" : "splines",
                "Spline Samples" : "splineSamples",
                "Surface Samples" : "surfaceSamples",
                "Cyclic" : "cyclic",
                "Smoothness" : "smoothness"}

    def getOutputSocketNames(self):
        return {"Vertices" : "vertices",
                "Polygons" : "polygons"}

    def execute(self, splines, splineSamples, surfaceSamples, cyclic, smoothness):
        def canExecute():
            for spline in splines:
                if not spline.isEvaluable: return False
            if len(splines) < 2: return False
            if splineSamples < 2: return False
            if surfaceSamples < 2: return False
            if cyclic and surfaceSamples < 3: return False
            return True
            
        for spline in splines:
            spline.update()
        
        if canExecute():
            vertices, polygons = loftSplines(splines, 
                                             splineSamples, surfaceSamples, 
                                             self.interpolationType, cyclic, smoothness)
            return vertices, polygons
        else: return [], []
