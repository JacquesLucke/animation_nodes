import bpy
from bpy.props import *
from ... utils.layout import writeText
from ... base_types.node import AnimationNode

class TextSequenceOutputNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_TextSequenceOutputNode"
    bl_label = "Text Sequence Output"

    errorMessage = StringProperty()

    def create(self):
        self.inputs.new("an_SequenceSocket", "Sequence", "sequence").defaultDrawType = "PROPERTY_ONLY"
        self.inputs.new("an_StringSocket", "Text", "text")
        self.inputs.new("an_IntegerSocket", "Size", "size").value = 200
        self.inputs.new("an_BooleanSocket", "Shadow", "shadow").value = False
        self.inputs.new("an_StringSocket", "Align", "align")
        self.inputs.new("an_FloatSocket", "X Location", "xLocation").value = 0.5
        self.inputs.new("an_FloatSocket", "Y Location", "yLocation").value = 0.0
        self.outputs.new("an_SequenceSocket", "Sequence", "sequence")

        for socket in self.inputs[1:]:
            socket.defaultDrawType = "TEXT_ONLY"
        for socket in self.inputs[4:]:
            socket.hide = True

    def draw(self, layout):
        if self.errorMessage != "":
            writeText(layout, self.errorMessage, width = 25, icon = "ERROR")

    def drawAdvanced(self, layout):
        layout.label("This node uses only linked inputs!", icon = "INFO")
        writeText(layout, "Possible values for 'Align' are 'LEFT', 'CENTER' and 'RIGHT'")

    def getExecutionCode(self):
        isLinked = self.getLinkedInputsDict()
        lines = []
        lines.append("if getattr(sequence, 'type', '') == 'TEXT':")

        if isLinked["text"]: lines.append("    sequence.text = text")
        if isLinked["size"]: lines.append("    sequence.font_size = size")
        if isLinked["shadow"]: lines.append("    sequence.use_shadow = shadow")
        if isLinked["align"]: lines.append("    self.setAlignment(sequence, align)")
        if isLinked["xLocation"]: lines.append("    sequence.location[0] = xLocation")
        if isLinked["yLocation"]: lines.append("    sequence.location[1] = yLocation")

        lines.append("    pass")

        return lines

    def setAlignment(self, sequence, align):
        if align in ("LEFT", "CENTER", "RIGHT"):
            sequence.align = align
            self.errorMessage = ""
        else:
            self.errorMessage = "The align type is invalid. Look in the advanced panels to see the possibilities."
