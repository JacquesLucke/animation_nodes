import bpy
from ... data_structures import VirtualDoubleList
from ... base_types import AnimationNode, VectorizedSocket
from ... algorithms.spline.bevel_poly_spline import bevelPolySpline

class BevelSplineNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_BevelSplineNode"
    bl_label = "Bevel Spline"
    errorHandlingType = "EXCEPTION"

    useRadiusList: VectorizedSocket.newProperty()

    def create(self):
        self.newInput("Spline", "Spline", "spline", defaultDrawType = "PROPERTY_ONLY")

        self.newInput(VectorizedSocket("Float", "useRadiusList",
            ("Radius", "radius", dict(value = 0.5, minValue = 0)),
            ("Radii", "radii")))

        self.newOutput("Spline", "Spline", "spline")

    def execute(self, spline, radii):
        if spline.type != "POLY":
            self.raiseErrorMessage("Bezier splines are not supported!")
        return bevelPolySpline(spline, VirtualDoubleList.create(radii, 0.5))
