import bpy
from ... base_types.node import AnimationNode
from ... algorithms.interpolation import linear, fCurveMapping

class InterpolationFromFCurveNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_InterpolationFromFCurveNode"
    bl_label = "Interpolation from FCurve"

    def create(self):
        self.inputs.new("an_FCurveSocket", "FCurve", "fCurve")
        self.outputs.new("an_InterpolationSocket", "Interpolation", "interpolation")

    def execute(self, fCurve):
        if fCurve is None: return (linear, None)
        startX, endX = fCurve.range()
        if startX == endX: return (linear, None)
        startY = fCurve.evaluate(startX)
        endY = fCurve.evaluate(endX)
        if startY == endY: return (linear, None)

        return (fCurveMapping, (fCurve, startX, endX - startX, -startY, endY - startY))
