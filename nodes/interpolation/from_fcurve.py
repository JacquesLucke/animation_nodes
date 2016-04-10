import bpy
from ... base_types.node import AnimationNode
from ... algorithms.interpolation import linear, fCurveMapping, assignArguments

class InterpolationFromFCurveNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_InterpolationFromFCurveNode"
    bl_label = "Interpolation from FCurve"

    def create(self):
        self.newInput("an_FCurveSocket", "FCurve", "fCurve")
        self.newOutput("an_InterpolationSocket", "Interpolation", "interpolation")

    def execute(self, fCurve):
        if fCurve is None: return linear
        startX, endX = fCurve.range()
        if startX == endX: return linear
        startY = fCurve.evaluate(startX)
        endY = fCurve.evaluate(endX)
        if startY == endY: return linear
        
        return assignArguments(fCurveMapping, (fCurve, startX, endX - startX, -startY, endY - startY))
