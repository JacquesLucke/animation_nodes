import bpy
from bpy.props import *
from ... utils.layout import writeText
from ... base_types.node import AnimationNode

soundTypeItems = [
    ("SINGLE", "Single", ""),
    ("EQUALIZER", "Equalizer", "")]

class SoundFromSequencesNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_SoundFromSequencesNode"
    bl_label = "Sound from Sequences"

    soundType = EnumProperty(name = "Sound Type", items = soundTypeItems)
    errorMessage = StringProperty()

    def create(self):
        self.width = 160
        self.inputs.new("an_SequenceListSocket", "Sequences", "sequences")
        self.inputs.new("an_IntegerSocket", "Bake Index", "bakeIndex")
        self.outputs.new("an_SoundSocket", "Sound", "sound")

    def draw(self, layout):
        layout.prop(self, "soundType")
        if self.errorMessage != "":
            writeText(layout, self.errorMessage, width = 25, icon = "ERROR")

    def execute(self, sequences, bakeIndex):
        try:
            self.errorMessage = ""
            if self.soundType == "SINGLE": return SingleSoundEvaluator(sequences, bakeIndex)
            if self.soundType == "EQUALIZER": return EqualizerSoundEvaluator(sequences, bakeIndex)
        except IndexError:
            self.errorMessage = "At least one sequence does not have this bake index"
            return None


class SingleSoundEvaluator:
    type = "SINGLE"

    def __init__(self, sequences, index):
        self.sequenceData = [(sequence, sequence.sound.singleData[index]) for sequence in sequences if getattr(sequence, "type", "") == "SOUND"]

    def evaluate(self, frame):
        intFrame = int(frame)
        if intFrame == frame:
            return self.evaluateInt(intFrame)
        else:
            before = self.evaluateInt(intFrame)
            after = self.evaluateInt(intFrame + 1)
            influence = frame - intFrame
            return before * (1 - influence) + after * influence

    def evaluateInt(self, frame):
        evaluate = self.evaluateSequence
        return sum([evaluate(sequence, data, frame) for sequence, data in self.sequenceData])

    def evaluateSequence(self, sequence, data, frame):
        if sequence.frame_final_start <= frame < sequence.frame_final_end - 1:
            return data.samples[frame - sequence.frame_start].strength
        return 0

class EqualizerSoundEvaluator:
    type = "EQUALIZER"

    def __init__(self, sequences, index):
        self.sequenceData = [(sequence, sequence.sound.equalizerData[index]) for sequence in sequences if getattr(sequence, "type", "") == "SOUND"]

    def evaluate(self, frame):
        return self.evaluateInt(int(frame))

    def evaluateInt(self, frame):
        evaluate = self.evaluateSequence
        strengths = [evaluate(sequence, data, frame) for sequence, data in self.sequenceData]
        return [sum(s) for s in zip(*strengths)]

    def evaluateSequence(self, sequence, data, frame):
        if sequence.frame_final_start <= frame < sequence.frame_final_end - 1:
            return [sample.strength for sample in data.samples[frame - sequence.frame_start].samples]
        return [0.0] * data.frequencyAmount
