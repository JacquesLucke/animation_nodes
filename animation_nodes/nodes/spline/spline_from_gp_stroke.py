import bpy
from ... data_structures import PolySpline
from ... base_types import AnimationNode, VectorizedSocket

class SplineFromGPStrokeNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_SplineFromGPStrokeNode"
    bl_label = "Spline From GP Stroke"
    codeEffects = [VectorizedSocket.CodeEffect]

    useStrokeList: VectorizedSocket.newProperty()

    def create(self):
        self.newInput(VectorizedSocket("GPStroke", "useStrokeList",
            ("Stroke", "stroke"), ("Strokes", "strokes")))

        self.newOutput(VectorizedSocket("Spline", "useStrokeList",
            ("Spline", "spline"), ("Splines", "splines")))

    def getExecutionCode(self, required):
        return "spline = self.splinesFromStrokes(stroke)"

    def splinesFromStrokes(self, stroke):
        if stroke is None: return PolySpline()

        return PolySpline(points = stroke.vertices.copy(),
                          radii = stroke.pressures.copy(),
                          cyclic = stroke.drawCyclic,
                          materialIndex = stroke.materialIndex)
