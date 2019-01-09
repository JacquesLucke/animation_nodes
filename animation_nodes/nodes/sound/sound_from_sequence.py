import bpy
from ... data_structures import Sound, SoundSequence
from ... base_types import AnimationNode, VectorizedSocket

class SoundFromSequenceNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_SoundFromSequenceNode"
    bl_label = "Sound From Sequence"

    multipleSequences: VectorizedSocket.newProperty()

    def create(self):
        self.newInput(VectorizedSocket("Sequence", "multipleSequences",
            ("Sequence", "sequence"), ("Sequences", "sequences")))

        self.newOutput("Sound", "Sound", "sound")

    def execute(self, sequences):
        if not self.multipleSequences: sequences = [sequences]
        return Sound([SoundSequence.fromSequence(s) for s in sequences if s is not None and s.type == "SOUND"])
