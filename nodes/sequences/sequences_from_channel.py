import bpy
from ... base_types.node import AnimationNode

class SequencesFromChannelNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_SequencesFromChannelNode"
    bl_label = "Sequences from Channel"

    def create(self):
        socket = self.newInput("an_IntegerSocket", "Channel", "channel")
        socket.value = 1
        socket.setRange(1, 32)
        self.newInput("an_SceneSocket", "Scene", "scene").hide = True
        self.newOutput("an_SequenceListSocket", "Sequences", "sequences")

    def getExecutionCode(self):
        return ("editor = scene.sequence_editor if scene else None",
                "sequences = [sequence for sequence in getattr(editor, 'sequences', []) if sequence.channel == channel]")
