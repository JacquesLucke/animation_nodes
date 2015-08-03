import bpy
from ... base_types.node import AnimationNode

class JoinStrings(bpy.types.Node, AnimationNode):
    bl_idname = "mn_JoinStrings"
    bl_label = "Join Texts"

    inputNames = { "Texts" : "texts",
                   "Separator" : "separator" }

    outputNames = { "Text" : "text" }

    def create(self):
        self.inputs.new("mn_StringListSocket", "Texts")
        self.inputs.new("mn_StringSocket", "Separator")
        self.outputs.new("mn_StringSocket", "Text")

    def getExecutionCode(self):
        return "$text$ = %separator%.join(%texts%)"
