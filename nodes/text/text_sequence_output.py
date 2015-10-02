import bpy
from bpy.props import *
from ... utils.layout import writeText
from ... base_types.node import AnimationNode

class TextSequenceOutputNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_TextSequenceOutputNode"
    bl_label = "Text Sequence Output"

    errorMessage = StringProperty()

    def create(self):
        self.width = 160
        self.inputs.new("an_SequenceSocket", "Sequence", "sequence").defaultDrawType = "PROPERTY_ONLY"
        self.inputs.new("an_StringSocket", "Text", "text")
        self.inputs.new("an_IntegerSocket", "Size", "size").value = 200
        self.inputs.new("an_BooleanSocket", "Shadow", "shadow").value = False
        self.inputs.new("an_StringSocket", "X Align", "xAlign").value = "CENTER"
        self.inputs.new("an_StringSocket", "Y Align", "yAlign").value = "BOTTOM"
        self.inputs.new("an_FloatSocket", "X Location", "xLocation").value = 0.5
        self.inputs.new("an_FloatSocket", "Y Location", "yLocation").value = 0.0
        self.inputs.new("an_FloatSocket", "Wrap Width", "wrapWidth").value = 0.0
        self.outputs.new("an_SequenceSocket", "Sequence", "sequence")

        for socket in self.inputs[1:]:
            socket.useIsUsedProperty = True
            socket.isUsed = False
        for socket in self.inputs[4:]:
            socket.hide = True

    def draw(self, layout):
        if self.errorMessage != "":
            writeText(layout, self.errorMessage, width = 25, icon = "ERROR")

    def drawAdvanced(self, layout):
        writeText(layout, "Possible values for 'X Align' are 'LEFT', 'CENTER' and 'RIGHT'")
        writeText(layout, "Possible values for 'Y Align' are 'TOP', 'CENTER' and 'BOTTOM'")

    def getExecutionCode(self):
        yield "if getattr(sequence, 'type', '') == 'TEXT':"
        yield "    self.errorMessage = ''"

        s = self.inputs
        if s["Text"].isUsed:        yield "    sequence.text = text"
        if s["Size"].isUsed:        yield "    sequence.font_size = size"
        if s["Shadow"].isUsed:      yield "    sequence.use_shadow = shadow"
        if s["X Align"].isUsed:       yield "    self.setXAlignment(sequence, xAlign)"
        if s["Y Align"].isUsed:       yield "    self.setYAlignment(sequence, yAlign)"
        if s["X Location"].isUsed:  yield "    sequence.location[0] = xLocation"
        if s["Y Location"].isUsed:  yield "    sequence.location[1] = yLocation"
        if s["Wrap Width"].isUsed:  yield "    sequence.wrap_width = wrapWidth"

    def setXAlignment(self, sequence, align):
        if align in ("LEFT", "CENTER", "RIGHT"):
            sequence.align_x = align
        else:
            self.errorMessage = "X Align must be LEFT, CENTER or RIGHT"

    def setYAlignment(self, sequence, align):
        if align in ("TOP", "CENTER", "BOTTOM"):
            sequence.align_y = align
        else:
            self.errorMessage = "Y Align must be TOP, CENTER or BOTTOM"
