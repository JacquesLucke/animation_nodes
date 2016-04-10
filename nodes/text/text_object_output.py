import bpy
from bpy.props import *
from ... utils.layout import writeText
from ... events import executionCodeChanged
from ... base_types.node import AnimationNode

class TextObjectOutputNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_TextObjectOutputNode"
    bl_label = "Text Object Output"
    bl_width_default = 170

    errorMessage = StringProperty()

    def create(self):
        self.newInput("an_ObjectSocket", "Object", "object").defaultDrawType = "PROPERTY_ONLY"

        self.newInput("an_StringSocket", "Text", "text")
        self.newInput("an_FloatSocket", "Size", "size").value = 1.0
        self.newInput("an_FloatSocket", "Extrude", "extrude")
        self.newInput("an_FloatSocket", "Shear", "shear")
        self.newInput("an_FloatSocket", "Bevel Depth", "bevelDepth")
        self.newInput("an_IntegerSocket", "Bevel Resolution", "bevelResolution")

        self.newInput("an_FloatSocket", "Letter Spacing", "letterSpacing").value = 1.0
        self.newInput("an_FloatSocket", "Word Spacing", "wordSpacing").value = 1.0
        self.newInput("an_FloatSocket", "Line Spacing", "lineSpacing").value = 1.0

        self.newInput("an_FloatSocket", "X Offset", "xOffset")
        self.newInput("an_FloatSocket", "Y Offset", "yOffset")
        self.newInput("an_StringSocket", "Align", "align").value = "CENTER"

        self.newInput("an_FontSocket", "Font", "font")
        self.newInput("an_FontSocket", "Bold Font", "fontBold")
        self.newInput("an_FontSocket", "Italic Font", "fontItalic")
        self.newInput("an_FontSocket", "Bold Italic Font", "fontBoldItalic")

        for socket in self.inputs[1:]:
            socket.useIsUsedProperty = True
            socket.isUsed = False
        for socket in self.inputs[4:]:
            socket.hide = True

        self.newOutput("an_ObjectSocket", "Object", "object")

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

        if s["Font"].isUsed:                yield "    textObject.font = font"
        if s["Bold Font"].isUsed:           yield "    textObject.font_bold = fontBold"
        if s["Italic Font"].isUsed:         yield "    textObject.font_italic = fontItalic"
        if s["Bold Italic Font"].isUsed:    yield "    textObject.font_bold_italic = fontBoldItalic"

    def setAlignment(self, textObject, align):
        if align in ("LEFT", "CENTER", "RIGHT", "JUSTIFY", "FLUSH"):
            textObject.align = align
            self.errorMessage = ""
        else:
            self.errorMessage = "The align type is invalid. Look in the advanced panels to see all possible values."
