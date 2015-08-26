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

    def settingChanged(self, context):
        self.inputs["Smoothness"].hide = self.interpolationType != "BEZIER"
        propertyChanged(self, context)

    interpolationType = EnumProperty(name = "Interpolation Type", default = "BEZIER", items = interpolationTypeItems, update = settingChanged)

    resolution = IntProperty(name = "Resolution", default = 100, min = 2, description = "Increase to have a more accurate evaluation", update = propertyChanged)
    splineDistributionType = EnumProperty(name = "Spline Distribution", default = "RESOLUTION", items = sampleDistributionTypeItems, update = propertyChanged)
    surfaceDistributionType = EnumProperty(name = "Surface Distribution", default = "RESOLUTION", items = sampleDistributionTypeItems, update = propertyChanged)

    def create(self):
        self.inputs.new("an_SplineListSocket", "Splines", "splines")
        socket1 = self.inputs.new("an_IntegerSocket", "Spline Samples", "splineSamples")
        socket2 = self.inputs.new("an_IntegerSocket", "Surface Samples", "surfaceSamples")
        for socket in (socket1, socket2):
            socket.value = 16
            socket.setMinMax(2, 100000)
        self.inputs.new("an_BooleanSocket", "Cyclic", "cyclic").value = False
        self.inputs.new("an_FloatSocket", "Smoothness", "smoothness").value = 0.3333
        socket = self.inputs.new("an_FloatSocket", "Start", "start")
        socket.value, socket.hide = 0.0, True
        socket.setMinMax(0.0, 1.0)
        socket = self.inputs.new("an_FloatSocket", "End", "end")
        socket.value, socket.hide = 1.0, True
        socket.setMinMax(0.0, 1.0)
        self.outputs.new("an_VectorListSocket", "Vertices", "vertices")
        self.outputs.new("an_PolygonIndicesListSocket", "Polygons", "polygons")
        self.width += 20
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

        for spline in splines:
            spline.update()

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
