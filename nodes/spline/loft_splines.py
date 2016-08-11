import bpy
from bpy.props import *
from ... events import propertyChanged
from ... base_types.node import AnimationNode
from ... algorithms.mesh_generation.from_splines import loftSplines

interpolationTypeItems = [
    ("LINEAR", "Linear", ""),
    ("BEZIER", "Bezier", "")]

sampleDistributionTypeItems = [
    ("RESOLUTION", "Resolution", ""),
    ("UNIFORM", "Uniform", "")]

class LoftSplinesNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_LoftSplinesNode"
    bl_label = "Loft Splines"
    bl_width_default = 160

    def settingChanged(self, context):
        self.inputs["Smoothness"].hide = self.interpolationType != "BEZIER"
        propertyChanged(self, context)

    interpolationType = EnumProperty(name = "Interpolation Type", default = "BEZIER",
        items = interpolationTypeItems, update = settingChanged)

    resolution = IntProperty(name = "Resolution", default = 100, min = 2,
        description = "Increase to have a more accurate evaluation", update = propertyChanged)

    splineDistributionType = EnumProperty(name = "Spline Distribution", default = "RESOLUTION",
        items = sampleDistributionTypeItems, update = propertyChanged)

    surfaceDistributionType = EnumProperty(name = "Surface Distribution", default = "RESOLUTION",
        items = sampleDistributionTypeItems, update = propertyChanged)

    def create(self):
        self.newInput("Spline List", "Splines", "splines")
        socket1 = self.newInput("Integer", "Spline Samples", "splineSamples")
        socket2 = self.newInput("Integer", "Surface Samples", "surfaceSamples")
        for socket in (socket1, socket2):
            socket.value = 16
            socket.minValue = 2
        self.newInput("Boolean", "Cyclic", "cyclic").value = False
        self.newInput("Float", "Smoothness", "smoothness").value = 0.3333
        self.newInput("Float", "Start", "start", hide = True, value = 0.0).setRange(0.0, 1.0)
        self.newInput("Float", "End", "end", hide = True, value = 1.0).setRange(0.0, 1.0)
        self.newOutput("Vector List", "Vertices", "vertices")
        self.newOutput("Polygon Indices List", "Polygons", "polygons")
        self.settingChanged(bpy.context)

    def draw(self, layout):
        layout.prop(self, "interpolationType", text = "")

    def drawAdvanced(self, layout):
        col = layout.column()
        col.prop(self, "splineDistributionType")
        col.prop(self, "surfaceDistributionType")
        col.prop(self, "resolution")

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

        if canExecute():
            vertices, polygons = loftSplines(splines,
                                             splineSamples,
                                             surfaceSamples,
                                             type = self.interpolationType,
                                             cyclic = cyclic,
                                             smoothness = smoothness,
                                             uniformConverterResolution = self.resolution,
                                             splineDistributionType = self.splineDistributionType,
                                             surfaceDistributionType = self.surfaceDistributionType,
                                             startSurfaceParameter = start,
                                             endSurfaceParameter = end)
            return vertices, polygons
        else: return [], []
