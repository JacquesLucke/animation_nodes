import bpy
from ... base_types.node import AnimationNode

class EvaluateFCurveNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_EvaluateFCurveNode"
    bl_label = "Evaluate FCurve"

    def create(self):
        self.inputs.new("an_FCurveSocket", "FCurve", "fCurve")
        self.inputs.new("an_FloatSocket", "Frame", "frame")
        self.outputs.new("an_GenericSocket", "Value", "value")

    def getExecutionCode(self):
        yield "if fCurve is None: value = None"
        yield "else: value = fCurve.evaluate(frame)"
