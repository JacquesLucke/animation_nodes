import bpy
from ... base_types.node import AnimationNode

class GetAllSequencesNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_GetAllSequencesNode"
    bl_label = "Get all Sequences"

    def create(self):
        self.outputs.new("an_SequenceListSocket", "Sequences", "sequences")

    def getExecutionCode(self):
        return ("editor = bpy.context.scene.sequence_editor",
                "sequences = list(editor.sequences) if editor else []")
