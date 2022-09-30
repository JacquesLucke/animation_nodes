import bpy
from ... data_structures import Sound, SoundSequence
from ... base_types import AnimationNode, VectorizedSocket

class SoundFromSequenceNode(AnimationNode, bpy.types.Node):
    bl_idname = "an_SoundFromSequenceNode"
    bl_label = "Sound From Sequence"

    useSequenceList: VectorizedSocket.newProperty()

    def create(self):
        self.newInput(VectorizedSocket("Sequence", "useSequenceList",
            ("Sequence", "sequence"), ("Sequences", "sequences")))

        self.newOutput("Sound", "Sound", "sound")

    def execute(self, sequences):
        if not self.useSequenceList: sequences = [sequences]
        return Sound([SoundSequence.fromSequence(s) for s in sequences if s is not None and s.type == "SOUND"])
