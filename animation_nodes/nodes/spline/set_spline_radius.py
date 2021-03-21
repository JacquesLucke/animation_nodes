import bpy
from bpy.props import *
from ... events import executionCodeChanged
from ... base_types import AnimationNode, VectorizedSocket
from ... data_structures import VirtualFloatList, VirtualDoubleList, FloatList

vectorizationTypeItems = [
    ("RADIUS_PER_POINT", "Radius Per Point", "Set the radius per point", "NONE", 0),
    ("RADIUS_PER_SPLINE", "Radius Per Spline", "Set the radius per spline", "NONE", 1),
]

class SetSplineRadiusNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_SetSplineRadiusNode"
    bl_label = "Set Spline Radius"

    useSplineList: VectorizedSocket.newProperty()
    useRadiusList: VectorizedSocket.newProperty()

    vectorizationType: EnumProperty(name = "Vectorization Type", default = "RADIUS_PER_POINT",
        items = vectorizationTypeItems, update = executionCodeChanged
    )

    def create(self):
        socket = self.newInput(VectorizedSocket("Spline", "useSplineList",
            ("Spline", "spline"), ("Splines", "splines")))
        socket.defaultDrawType = "PROPERTY_ONLY"
        socket.dataIsModified = True

        self.newInput(VectorizedSocket("Float", "useRadiusList",
            ("Radius", "radius", dict(value = 0.1, minValue = 0)),
            ("Radii", "radii")))

        self.newOutput(VectorizedSocket("Spline", "useSplineList",
            ("Spline", "spline"),
            ("Splines", "splines")))

    def draw(self, layout):
        if self.useSplineList and self.useRadiusList:
            layout.prop(self, "vectorizationType", text = "")

    def getExecutionFunctionName(self):
        if self.useSplineList:
            if self.useRadiusList:
                if self.vectorizationType == "RADIUS_PER_POINT":
                    return "execute_MultipleSplines_MultipleRadii_PerPoint"
                else:
                    return "execute_MultipleSplines_MultipleRadii_PerSpline"
            else:
                return "execute_MultipleSplines_SingleRadius"
        else:
            if self.useRadiusList:
                return "execute_SingleSpline_MultipleRadii"
            else:
                return "execute_SingleSpline_SingleRadius"

    def execute_MultipleSplines_MultipleRadii_PerPoint(self, splines, radii):
        for spline in splines:
            self.execute_SingleSpline_MultipleRadii(spline, radii)
        return splines

    def execute_MultipleSplines_MultipleRadii_PerSpline(self, splines, radii):
        virtualRadii = VirtualDoubleList.create(radii, 0)
        for i, spline in enumerate(splines):
            self.execute_SingleSpline_SingleRadius(spline, virtualRadii[i])
        return splines

    def execute_MultipleSplines_SingleRadius(self, splines, radius):
        for spline in splines:
            self.execute_SingleSpline_SingleRadius(spline, radius)
        return splines

    def execute_SingleSpline_SingleRadius(self, spline, radius):
        spline.radii = FloatList.fromValue(radius, len(spline.points))
        return spline

    def execute_SingleSpline_MultipleRadii(self, spline, radii):
        virtualRadii = VirtualFloatList.create(FloatList.fromValues(radii), 0)
        spline.radii = virtualRadii.materialize(len(spline.points))
        return spline
