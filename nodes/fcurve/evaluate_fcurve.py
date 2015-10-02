import bpy
from bpy.props import *
from ... events import executionCodeChanged
from ... base_types.node import AnimationNode

frameTypeItems = [
    ("OFFSET", "Offset", ""),
    ("ABSOLUTE", "Absolute", "") ]

class EvaluateFCurveNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_EvaluateFCurveNode"
    bl_label = "Evaluate FCurve"

    frameType = EnumProperty(
        name = "Frame Type", default = "OFFSET",
        items = frameTypeItems, update = executionCodeChanged)

    def create(self):
        self.inputs.new("an_FCurveSocket", "FCurve", "fCurve")
        self.inputs.new("an_FloatSocket", "Frame", "frame")
        self.outputs.new("an_FloatSocket", "Value", "value")

    def draw(self, layout):
        layout.prop(self, "frameType", text = "Frame")

    def getExecutionCode(self):
        if self.frameType == "OFFSET": yield "evaluationFrame = frame + self.nodeTree.scene.frame_current_final"
        else: yield "evaluationFrame = frame"

        yield "if fCurve is None: value = None"
        yield "else: value = fCurve.evaluate(evaluationFrame)"
