import bpy
from ... data_structures import GPStroke, FloatList
from ... base_types import AnimationNode, VectorizedSocket

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

        vertices = spline.points.copy()
        pressures = spline.radii.copy()
        amount = len(vertices)
        strengths = FloatList(length = amount)
        uvRotations = FloatList(length = amount)
        strengths.fill(1)
        uvRotations.fill(0)
        return GPStroke(vertices = vertices, strengths = strengths,
                        pressures = pressures, uvRotations = uvRotations,
                        useCyclic = spline.cyclic)
