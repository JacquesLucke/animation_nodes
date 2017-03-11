import bpy
from bpy.props import *
from ... utils.layout import writeText
from ... base_types import AnimationNode
from ... data_structures import DoubleList, AverageSound

soundTypeItems = [
    ("AVERAGE", "Average", "", "FORCE_TURBULENCE", 0),
    ("SPECTRUM", "Spectrum", "", "RNDCURVE", 1)
]

class SoundFromSequencesNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_SoundFromSequencesNode"
    bl_label = "Sound from Sequences"
    bl_width_default = 160

    soundType = EnumProperty(name = "Sound Type", items = soundTypeItems)
    errorMessage = StringProperty()

    def create(self):
        self.newInput("Sequence List", "Sequences", "sequences")
        self.newInput("Integer", "Bake Index", "bakeIndex")
        self.newOutput("Sound", "Sound", "sound")

    def draw(self, layout):
        layout.prop(self, "soundType", text = "")
        if self.errorMessage != "":
            writeText(layout, self.errorMessage, width = 25, icon = "ERROR")

    def execute(self, sequences, bakeIndex):
        if len(sequences) == 0: return None
        try:
            self.errorMessage = ""
            if self.soundType == "AVERAGE": return AverageSound.fromSequences(sequences, bakeIndex)
            if self.soundType == "SPECTRUM": return SpectrumSoundEvaluator(sequences, bakeIndex)
        except IndexError:
            self.errorMessage = "At least one sequence does not have this bake index"
            return None

class SpectrumSoundEvaluator:
    type = "SPECTRUM"

    def __init__(self, sequences, index):
        self.sequenceData = [(sequence, sequence.sound.spectrumData[index]) for sequence in sequences if getattr(sequence, "type", "") == "SOUND"]

    def evaluate(self, frame):
        intFrame = int(frame)
        if intFrame == frame:
            return DoubleList.fromValues(self.evaluateInt(intFrame))
        else:
            before = self.evaluateInt(intFrame)
            after = self.evaluateInt(intFrame + 1)
            influence = frame - intFrame
            return DoubleList.fromValues([a * (1 - influence) + b * influence for a, b in zip(before, after)])

    def evaluateInt(self, frame):
        evaluate = self.evaluateSequence
        strengths = [evaluate(sequence, data, frame) for sequence, data in self.sequenceData]
        return [sum(s) for s in zip(*strengths)]

    def evaluateSequence(self, sequence, data, frame):
        if useSequenceForFrame(sequence, data, frame):
            return [sample.strength for sample in data.samples[frame - sequence.frame_start].samples]
        return [0.0] * data.frequencyAmount

def useSequenceForFrame(sequence, data, frame):
    return sequence.frame_final_start <= frame < min(sequence.frame_start + len(data.samples), sequence.frame_final_end)
