import bpy
from bpy.props import *
from ... mn_node_base import AnimationNode
from ... mn_execution import nodePropertyChanged, allowCompiling, forbidCompiling
from ... algorithms.mesh_generation.from_splines import loftSplines

interpolationTypeItems = [
    ("LINEAR", "Linear", ""),
    ("BEZIER", "Bezier", "")]
    
sampleDistributionTypeItems = [
    ("RESOLUTION", "Resolution", ""),
    ("UNIFORM", "Uniform", "")]    
    
class mn_LoftSplines(bpy.types.Node, AnimationNode):
    bl_idname = "mn_LoftSplines"
    bl_label = "Loft Splines"
    
    def settingChanged(self, context):
        self.inputs["Smoothness"].hide = self.interpolationType != "BEZIER"
        nodePropertyChanged(self, context)
        
    interpolationType = EnumProperty(name = "Interpolation Type", default = "BEZIER", items = interpolationTypeItems, update = settingChanged)
    
    resolution = IntProperty(name = "Resolution", default = 100, min = 2, description = "Increase to have a more accurate evaluation", update = nodePropertyChanged)
    splineDistributionType = EnumProperty(name = "Spline Distribution", default = "RESOLUTION", items = sampleDistributionTypeItems, update = nodePropertyChanged)
    surfaceDistributionType = EnumProperty(name = "Surface Distribution", default = "RESOLUTION", items = sampleDistributionTypeItems, update = nodePropertyChanged)
        
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
        socket = self.inputs.new("mn_FloatSocket", "Start")
        socket.number, socket.hide = 0.0, True
        socket.setMinMax(0.0, 1.0)
        socket = self.inputs.new("mn_FloatSocket", "End")
        socket.number, socket.hide = 1.0, True
        socket.setMinMax(0.0, 1.0)
        self.outputs.new("mn_VectorListSocket", "Vertices")
        self.outputs.new("mn_PolygonIndicesListSocket", "Polygons")
        self.width += 20
        self.settingChanged(context)
        allowCompiling()
        
    def draw_buttons(self, context, layout):
        layout.prop(self, "interpolationType", text = "")
        
    def draw_buttons_ext(self, context, layout):
        col = layout.column()
        col.prop(self, "splineDistributionType")
        col.prop(self, "surfaceDistributionType")
        col.prop(self, "resolution")

    def getInputSocketNames(self):
        return {"Splines" : "splines",
                "Spline Samples" : "splineSamples",
                "Surface Samples" : "surfaceSamples",
                "Cyclic" : "cyclic",
                "Smoothness" : "smoothness",
                "Start" : "start",
                "End" : "end"}

    def getOutputSocketNames(self):
        return {"Vertices" : "vertices",
                "Polygons" : "polygons"}

    def execute(self, splines, splineSamples, surfaceSamples, cyclic, smoothness, start, end):
        def canExecute():
            for spline in splines:
                if not spline.isEvaluable: return False
            if len(splines) < 2: return False
            if splineSamples < 2: return False
            if surfaceSamples < 2: return False
            isRealCyclic = cyclic and start == 0.0 and end == 1.0
            if isRealCyclic and surfaceSamples < 3: return False
            return True
            
        for spline in splines:
            spline.update()
        
        if canExecute():
            vertices, polygons = loftSplines(splines, 
                                             splineSamples,
                                             surfaceSamples, 
                                             self.interpolationType,
                                             cyclic,
                                             smoothness,
                                             uniformConverterResolution = self.resolution,
                                             splineDistributionType = self.splineDistributionType,
                                             surfaceDistributionType = self.surfaceDistributionType,
                                             startSurfaceParameter = start,
                                             endSurfaceParameter = end)
            return vertices, polygons
        else: return [], []
