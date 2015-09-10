import bpy
from ... base_types.node import AnimationNode

class EvaluateEqualizerNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_EvaluateEqualizerNode"
    bl_label = "Evaluate Equalizer"

    def create(self):
        self.inputs.new("an_SoundSocket", "Sound", "sound")
        self.inputs.new("an_FloatSocket", "Frame", "frame")
        self.outputs.new("an_FloatListSocket", "Strengths", "strengths")

    def execute(self, sound, frame):
        if sound is None: return []
        if sound.type != "Equalizer": return []
        return sound.evaluate(frame)
