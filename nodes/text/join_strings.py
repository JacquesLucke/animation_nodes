import bpy
from ... base_types.node import AnimationNode

class JoinStrings(bpy.types.Node, AnimationNode):
    bl_idname = "an_JoinStrings"
    bl_label = "Join Texts"

    inputNames = { "Texts" : "texts",
                   "Separator" : "separator" }

    outputNames = { "Text" : "text" }

    def create(self):
        self.inputs.new("an_StringListSocket", "Texts")
        self.inputs.new("an_StringSocket", "Separator")
        self.outputs.new("an_StringSocket", "Text")

    def getExecutionCode(self):
        return "$text$ = %separator%.join(%texts%)"
