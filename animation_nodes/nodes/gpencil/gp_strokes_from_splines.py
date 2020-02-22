import bpy
from ... base_types import AnimationNode, VectorizedSocket
from ... data_structures import GPStroke, VirtualDoubleList, DoubleList

class GPStrokesFromSplinesNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_GPStrokesFromSplinesNode"
    bl_label = "GP Strokes From Splines"
    codeEffects = [VectorizedSocket.CodeEffect]

    useSplineList: VectorizedSocket.newProperty()

    def create(self):
        socket = self.newInput(VectorizedSocket("Spline", "useSplineList",
            ("Spline", "spline"), ("Splines", "splines")))
        socket.defaultDrawType = "PROPERTY_ONLY"
        socket.dataIsModified = True

        self.newOutput(VectorizedSocket("GPStroke", "useSplineList",
            ("Stroke", "stroke"),
            ("Strokes", "strokes")))

    def getExecutionCode(self, required):
        return "stroke = self.strokesFromSplines(spline)"

    def strokesFromSplines(self, spline):
        if spline is None: return GPStroke()

        vertices = spline.points
        amount = len(vertices)
        strengths = VirtualDoubleList.create(1, 1).materialize(amount)
        pressures = DoubleList.fromValues(spline.radii)
        uvRotations = VirtualDoubleList.create(0, 0).materialize(amount)

        return GPStroke(vertices = vertices, strengths = strengths, pressures = pressures,
                        uvRotations = uvRotations, drawCyclic = spline.cyclic)
