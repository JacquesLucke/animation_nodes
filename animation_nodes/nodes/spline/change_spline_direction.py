import bpy
from ... data_structures import PolySpline, BezierSpline
from ... base_types import AnimationNode, VectorizedSocket

class ChangeSplineDirectionNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_ChangeSplineDirectionNode"
    bl_label = "Change Spline Direction"
    codeEffects = [VectorizedSocket.CodeEffect]

    useSplineList: VectorizedSocket.newProperty()

    def create(self):
        socket = self.newInput(VectorizedSocket("Spline", "useSplineList",
            ("Spline", "spline"), ("Splines", "splines")))
        socket.defaultDrawType = "PROPERTY_ONLY"
        socket.dataIsModified = True

        self.newOutput(VectorizedSocket("Spline", "useSplineList",
            ("Spline", "newSpline"),
            ("Splines", "newSplines")))

    def getExecutionCode(self, required):
        return "newSpline = self.changeSplineDirection(spline)"

    def changeSplineDirection(self, spline):
        if spline.type == "POLY":
            return PolySpline(points = spline.points.reversed(),
                              radii = spline.radii.reversed(),
                              tilts = spline.tilts.reversed(),
                              cyclic = spline.cyclic,
                              materialIndex = spline.materialIndex)
        elif spline.type == "BEZIER":
            return BezierSpline(points = spline.points.reversed(),
                                leftHandles = spline.rightHandles.reversed(),
                                rightHandles = spline.leftHandles.reversed(),
                                radii = spline.radii.reversed(),
                                tilts = spline.tilts.reversed(),
                                cyclic = spline.cyclic,
                                materialIndex = spline.materialIndex)
