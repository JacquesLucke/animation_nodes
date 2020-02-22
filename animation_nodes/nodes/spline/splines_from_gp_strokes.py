import bpy
from ... data_structures import PolySpline, FloatList
from ... base_types import AnimationNode, VectorizedSocket

class SplinesFromGPStrokesNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_SplinesFromGPStrokesNode"
    bl_label = "Splines From GP Strokes"
    codeEffects = [VectorizedSocket.CodeEffect]

    useStrokeList: VectorizedSocket.newProperty()

    def create(self):
        socket = self.newInput(VectorizedSocket("GPStroke", "useStrokeList",
            ("Stroke", "stroke"), ("Strokes", "strokes")))
        socket.dataIsModified = True

        self.newOutput(VectorizedSocket("Spline", "useStrokeList",
            ("Spline", "spline"), ("Splines", "splines")))

    def getExecutionCode(self, required):
        return "spline = self.splinesFromStrokes(stroke)"

    def splinesFromStrokes(self, stroke):
        if stroke is None: return PolySpline()
        radii = FloatList.fromValues(stroke.pressures)
        return PolySpline(points = stroke.vertices, radii = radii, cyclic = stroke.drawCyclic)
