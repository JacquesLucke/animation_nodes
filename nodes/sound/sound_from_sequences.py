import bpy
from bpy.props import *
from ... utils.layout import writeText
from ... base_types.node import AnimationNode

class SoundFromSequencesNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_SoundFromSequencesNode"
    bl_label = "Sound from Sequences"

    errorMessage = StringProperty()

    def create(self):
        self.width = 160
        self.inputs.new("an_SequenceListSocket", "Sequences", "sequences")
        self.inputs.new("an_IntegerSocket", "Bake Index", "bakeIndex")
        self.outputs.new("an_SoundSocket", "Sound", "sound")

    def draw(self, layout):
        if self.errorMessage != "":
            writeText(layout, self.errorMessage, width = 25, icon = "ERROR")

    def execute(self, sequences, bakeIndex):
        try:
            self.errorMessage = ""
            return SequencesEvaluator(sequences, bakeIndex)
        except IndexError:
            self.errorMessage = "At least one sequence does not have this bake index"
            return None


class SequencesEvaluator:
    type = "Single"

    def __init__(self, sequences, index):
        self.sequenceData = [(sequence, sequence.sound.bakeData[index]) for sequence in sequences if sequence]

    def evaluate(self, frame):
        evaluate = self.evaluateSequence
        return sum([evaluate(sequence, bakeData, frame) for sequence, bakeData in self.sequenceData])

    def evaluateSequence(self, sequence, bakeData, frame):
        if sequence.frame_final_start <= frame < sequence.frame_final_end - 1:
            return bakeData.samples[frame - sequence.frame_start].strength
        return 0
