import bpy
from ... data_structures import PolySpline, BezierSpline
from ... base_types import AnimationNode, VectorizedSocket

class ChangeSplineDirectionNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_ChangeSplineDirectionNode"
    bl_label = "Change Spline Direction"
    bl_width_default = 160

    useSplineList: VectorizedSocket.newProperty()

    def create(self):
        socket = self.newInput(VectorizedSocket("Spline", "useSplineList",
            ("Spline", "spline"), ("Splines", "splines")))
        socket.defaultDrawType = "PROPERTY_ONLY"
        socket.dataIsModified = True

        self.newOutput(VectorizedSocket("Spline", "useSplineList",
            ("Spline", "spline"),
            ("Splines", "newSplines")))

    def getExecutionFunctionName(self):
        if self.useSplineList:
            return "execute_MultipleSplines"
        else:
            return "execute_SingleSpline"

    def execute_SingleSpline(self, spline):
        return self.changeSplineDirection(spline)

    def execute_MultipleSplines(self, splines):
        newSplines = []
        for spline in splines:
            newSplines.append(self.changeSplineDirection(spline))
        return newSplines

    def changeSplineDirection(self, spline):
        if spline.type == "POLY":
            return PolySpline(points = spline.points.reversed(),
                              radii = spline.radii.reversed(),
                              tilts = spline.tilts.reversed(),
                              cyclic = spline.cyclic)
        elif spline.type == "BEZIER":
            return BezierSpline(points = spline.points.reversed(),
                                radii = spline.radii.reversed(),
                                tilts = spline.tilts.reversed(),
                                cyclic = spline.cyclic)
