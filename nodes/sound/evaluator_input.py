import bpy
from bpy.props import *
from ... base_types.node import AnimationNode

evaluatorTypeItems = [
    ("SEQUENCE", "Sequence", ""),
    ("CHANNEL", "Channel", ""),
    ("ALL", "All", "") ]

class SoundEvaluatorInputNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_SoundEvaluatorInputNode"
    bl_label = "Sound Evaluator Input"

    evaluatorType = EnumProperty(name = "Type", default = "SEQUENCE", items = evaluatorTypeItems)

    def create(self):
        self.inputs.new("an_SequenceSocket", "Sequence", "sequence")
        self.inputs.new("an_IntegerSocket", "Bake Data Index", "bakeDataIndex")
        self.outputs.new("an_SoundSocket", "Sound", "sound")

    def draw(self, layout):
        layout.prop(self, "evaluatorType", text = "")

    def execute(self, sequence, bakeDataIndex):
        try: return SequenceEvaluator(sequence, bakeDataIndex)
        except: return None


class SequenceEvaluator:
    type = "Single"

    def __init__(self, sequence, index):
        self.sequence = sequence
        self.bakeData = sequence.sound.bakeData[index]

    def evaluate(self, frame):
        if self.sequence.frame_final_start <= frame < self.sequence.frame_final_end - 1:
            return self.bakeData.samples[frame - self.sequence.frame_start].strength
        return 0
