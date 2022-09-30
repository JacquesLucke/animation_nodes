import bpy
from bpy.props import *
from . c_utils import tiltSplinePoints
from ... events import propertyChanged
from ... base_types import AnimationNode, VectorizedSocket
from ... data_structures import VirtualFloatList, FloatList

class TiltSplineNode(AnimationNode, bpy.types.Node):
    bl_idname = "an_TiltSplineNode"
    bl_label = "Tilt Spline"

    useTiltList: VectorizedSocket.newProperty()
    useSplineList: VectorizedSocket.newProperty()

    accumulateTilts: BoolProperty(name = "Accumulate Tilts", default = False,
        update = propertyChanged)

    def create(self):
        socket = self.newInput(VectorizedSocket("Spline", "useSplineList",
            ("Spline", "spline"), ("Splines", "splines")))
        socket.defaultDrawType = "PROPERTY_ONLY"
        socket.dataIsModified = True

        self.newInput(VectorizedSocket("Float", "useTiltList",
            ("Tilt", "tilt"), ("Tilts", "tilts")))

        self.newOutput(VectorizedSocket("Spline", "useSplineList",
            ("Spline", "spline"),
            ("Splines", "splines")))

    def draw(self, layout):
        layout.prop(self, "accumulateTilts", text = "Accumulate")

    def getExecutionFunctionName(self):
        if self.useSplineList:
            if self.useTiltList:
                return "execute_MultipleSplines_MultipleTilts"
            else:
                return "execute_MultipleSplines_SingleTilt"
        else:
            if self.useTiltList:
                return "execute_SingleSpline_MultipleTilts"
            else:
                return "execute_SingleSpline_SingleTilt"

    def execute_MultipleSplines_MultipleTilts(self, splines, tilts):
        for spline in splines:
            self.execute_SingleSpline_MultipleTilts(spline, tilts)
        return splines

    def execute_MultipleSplines_SingleTilt(self, splines, tilt):
        for spline in splines:
            self.execute_SingleSpline_SingleTilt(spline, tilt)
        return splines

    def execute_SingleSpline_SingleTilt(self, spline, tilt):
        _tilts = VirtualFloatList.fromElement(tilt)
        tiltSplinePoints(spline, _tilts, self.accumulateTilts)
        return spline

    def execute_SingleSpline_MultipleTilts(self, spline, tilts):
        _tilts = VirtualFloatList.fromList(FloatList.fromValues(tilts), 0)
        tiltSplinePoints(spline, _tilts, self.accumulateTilts)
        return spline
