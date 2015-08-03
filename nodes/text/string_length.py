import bpy
from ... base_types.node import AnimationNode

class StringLengthNode(bpy.types.Node, AnimationNode):
    bl_idname = "mn_StringLengthNode"
    bl_label = "Text Length"

    inputNames = { "Text" : "text" }
    outputNames = { "Length" : "length" }

    def create(self):
        self.inputs.new("mn_StringSocket", "Text")
        self.outputs.new("mn_IntegerSocket", "Length")

    def getExecutionCode(self):
        return "$length$ = len(%text%)"
