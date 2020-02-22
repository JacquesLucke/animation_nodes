import bpy
from ... base_types import AnimationNode, VectorizedSocket
from ... data_structures import GPStroke, VirtualFloatList

class GPStrokeFromSplineNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_GPStrokeFromSplineNode"
    bl_label = "GP Stroke From Spline"
    codeEffects = [VectorizedSocket.CodeEffect]

    useSplineList: VectorizedSocket.newProperty()

    def create(self):
        socket = self.newInput(VectorizedSocket("Spline", "useSplineList",
            ("Spline", "spline"), ("Splines", "splines")))
        socket.defaultDrawType = "PROPERTY_ONLY"

        self.newOutput(VectorizedSocket("GPStroke", "useSplineList",
            ("Stroke", "stroke"),
            ("Strokes", "strokes")))

    def getExecutionCode(self, required):
        return "stroke = self.strokesFromSplines(spline)"

    def strokesFromSplines(self, spline):
        if spline is None: return GPStroke()

        vertices = spline.points
        amount = len(vertices)
        pressures = spline.radii
        strengths = VirtualFloatList.create(1, 1).materialize(amount)
        uvRotations = VirtualFloatList.create(0, 0).materialize(amount)

        return GPStroke(vertices = vertices, strengths = strengths, pressures = pressures,
                        uvRotations = uvRotations, drawCyclic = spline.cyclic)
