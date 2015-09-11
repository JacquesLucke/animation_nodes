import bpy
from ... base_types.node import AnimationNode

class GetAllSequencesNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_GetAllSequencesNode"
    bl_label = "Get All Sequences"

    def create(self):
        self.inputs.new("an_SceneSocket", "Scene", "scene").hide = True
        self.outputs.new("an_SequenceListSocket", "Sequences", "sequences")

    def getExecutionCode(self):
        return ("editor = scene.sequence_editor if scene else None",
                "sequences = getattr(editor, 'sequences', [])")
