import bpy
from bpy.props import *
from ... utils.layout import writeText
from ... events import executionCodeChanged
from ... base_types.node import AnimationNode

class TextObjectOutputNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_TextObjectOutputNode"
    bl_label = "Text Object Output"

    errorMessage = StringProperty()

    def create(self):
        self.inputs.new("an_ObjectSocket", "Object", "object").defaultDrawType = "PROPERTY_ONLY"

        self.inputs.new("an_StringSocket", "Text", "text")
        self.inputs.new("an_FloatSocket", "Size", "size").value = 1.0
        self.inputs.new("an_FloatSocket", "Extrude", "extrude")
        self.inputs.new("an_FloatSocket", "Shear", "shear")
        self.inputs.new("an_FloatSocket", "Bevel Depth", "bevelDepth")
        self.inputs.new("an_IntegerSocket", "Bevel Resolution", "bevelResolution")

        self.inputs.new("an_FloatSocket", "Letter Spacing", "letterSpacing").value = 1.0
        self.inputs.new("an_FloatSocket", "Word Spacing", "wordSpacing").value = 1.0
        self.inputs.new("an_FloatSocket", "Line Spacing", "lineSpacing").value = 1.0

        self.inputs.new("an_FloatSocket", "X Offset", "xOffset")
        self.inputs.new("an_FloatSocket", "Y Offset", "yOffset")
        self.inputs.new("an_StringSocket", "Align", "align").value = "CENTER"

        for socket in self.inputs[1:]:
            socket.useIsUsedProperty = True
            socket.isUsed = False
        for socket in self.inputs[4:]:
            socket.hide = True

        self.outputs.new("an_ObjectSocket", "Object", "object")
        self.width = 170

    def draw(self, layout):
        if self.errorMessage != "":
            writeText(layout, self.errorMessage, width = 25, icon = "ERROR")

    def drawAdvanced(self, layout):
        writeText(layout, "Possible values for 'Align' are 'LEFT', 'CENTER', 'RIGHT', 'JUSTIFY' and 'FLUSH'")

    def getExecutionCode(self):
        yield "if getattr(object, 'type', '') == 'FONT':"
        yield "    textObject = object.data"

        s = self.inputs
        if s["Text"].isUsed:                yield "    textObject.body = text"
        if s["Size"].isUsed:                yield "    textObject.size = size"
        if s["Extrude"].isUsed:             yield "    textObject.extrude = extrude"
        if s["Shear"].isUsed:               yield "    textObject.shear = shear"
        if s["Bevel Depth"].isUsed:         yield "    textObject.bevel_depth = bevelDepth"
        if s["Bevel Resolution"].isUsed:    yield "    textObject.bevel_resolution = bevelResolution"

        if s["Letter Spacing"].isUsed:      yield "    textObject.space_character = letterSpacing"
        if s["Word Spacing"].isUsed:        yield "    textObject.space_word = wordSpacing"
        if s["Line Spacing"].isUsed:        yield "    textObject.space_line = lineSpacing"

        if s["X Offset"].isUsed:            yield "    textObject.offset_x = xOffset"
        if s["Y Offset"].isUsed:            yield "    textObject.offset_y = yOffset"
        if s["Align"].isUsed:               yield "    self.setAlignment(textObject, align)"

    def setAlignment(self, textObject, align):
        if align in ("LEFT", "CENTER", "RIGHT", "JUSTIFY", "FLUSH"):
            textObject.align = align
            self.errorMessage = ""
        else:
            self.errorMessage = "The align type is invalid. Look in the advanced panels to see all possible values."
