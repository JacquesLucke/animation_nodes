import bpy
from ... base_types.node import AnimationNode

class StringLengthNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_StringLengthNode"
    bl_label = "Text Length"

    inputNames = { "Text" : "text" }
    outputNames = { "Length" : "length" }

    def create(self):
        self.inputs.new("an_StringSocket", "Text")
        self.outputs.new("an_IntegerSocket", "Length")

    def getExecutionCode(self):
        return "$length$ = len(%text%)"
