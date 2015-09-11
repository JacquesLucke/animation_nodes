import bpy
from ... base_types.node import AnimationNode

class SequencesFromChannelNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_SequencesFromChannelNode"
    bl_label = "Sequences from Channel"

    def create(self):
        socket = self.inputs.new("an_IntegerSocket", "Channel", "channel")
        socket.value = 1
        socket.setRange(1, 32)
        self.outputs.new("an_SequenceListSocket", "Sequences", "sequences")

    def getExecutionCode(self):
        return ("editor = bpy.context.scene.sequence_editor",
                "if editor: sequences = [sequence for sequence in editor.sequences if sequence.channel == channel]",
                "else: sequences = []")
