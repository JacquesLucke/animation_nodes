import bpy
from ... base_types.node import AnimationNode

class FCurveKeyframesNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_FCurveKeyframesNode"
    bl_label = "FCurve Keyframes"

    def create(self):
        self.inputs.new("an_FCurveSocket", "FCurve", "fCurve")
        self.outputs.new("an_FloatListSocket", "Keyframes Frames", "keyframesFrames")
        self.outputs.new("an_FloatListSocket", "Keyframes Values", "keyframesValues")

    def getExecutionCode(self):
        isLinked = self.getLinkedOutputsDict()
        if not any(isLinked.values()): return

        yield "if fCurve is not None:"
        if isLinked["keyframesFrames"]: yield "    keyframesFrames = [point.co[0] for point in fCurve.keyframe_points]"
        if isLinked["keyframesValues"]: yield "    keyframesValues = [point.co[1] for point in fCurve.keyframe_points]"
        yield "else: keyframesFrames, keyframesValues = [], []"
