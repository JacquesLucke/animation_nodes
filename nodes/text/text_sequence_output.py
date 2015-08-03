import bpy
from ... base_types.node import AnimationNode

class TextSequenceOutput(bpy.types.Node, AnimationNode):
    bl_idname = "mn_TextSequenceOutput"
    bl_label = "Text Sequence Output"

    inputNames = { "Sequence" : "sequence",
                   "Text" : "text",
                   "Size" : "size",
                   "Shadow" : "shadow",
                   "Align" : "align",
                   "X Location" : "xLocation",
                   "Y Location" : "yLocation" }

    outputNames = { "Sequence" : "sequence" }

    def create(self):
        self.inputs.new("mn_SequenceSocket", "Sequence").showName = False
        self.inputs.new("mn_StringSocket", "Text")
        self.inputs.new("mn_IntegerSocket", "Size").number = 200
        self.inputs.new("mn_BooleanSocket", "Shadow").value = False
        socket = self.inputs.new("mn_StringSocket", "Align")
        socket.useEnum = True
        socket.setEnumItems([("CENTER", "Center"), ("LEFT", "Left"), ("RIGHT", "Right")])
        socket.string = "CENTER"
        self.inputs.new("mn_FloatSocket", "X Location").number = 0.5
        self.inputs.new("mn_FloatSocket", "Y Location").number = 0.0
        self.outputs.new("mn_SequenceSocket", "Sequence")

    def execute(self, sequence, text, size, shadow, align, xLocation, yLocation):
        if getattr(sequence, "type", "") != "TEXT": return sequence

        sequence.text = text
        sequence.font_size = size
        sequence.use_shadow = shadow
        sequence.location[0] = xLocation
        sequence.location[1] = yLocation
        if align in ("CENTER", "LEFT", "RIGHT"):
            sequence.align = align

        return sequence
