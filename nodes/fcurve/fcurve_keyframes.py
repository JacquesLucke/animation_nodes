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
        yield "    keyframesFrames = []"
        yield "    keyframesValues = []"
        yield "    for point in fCurve.keyframe_points:"
        if isLinked["keyframesFrames"]: yield " " * 8 + "keyframesFrames.append(point.co[0])"
        if isLinked["keyframesValues"]: yield " " * 8 + "keyframesValues.append(point.co[1])"