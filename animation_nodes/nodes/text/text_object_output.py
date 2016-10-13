import bpy
from bpy.props import *
from ... utils.layout import writeText
from ... events import executionCodeChanged
from ... base_types import AnimationNode

class TextObjectOutputNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_TextObjectOutputNode"
    bl_label = "Text Object Output"
    bl_width_default = 170

    errorMessage = StringProperty()

    def create(self):
        self.newInput("Object", "Object", "object", defaultDrawType = "PROPERTY_ONLY")

        self.newInput("Text", "Text", "text")
        self.newInput("Float", "Size", "size", value = 1.0)
        self.newInput("Float", "Extrude", "extrude")
        self.newInput("Float", "Shear", "shear")
        self.newInput("Float", "Bevel Depth", "bevelDepth")
        self.newInput("Integer", "Bevel Resolution", "bevelResolution")

        self.newInput("Float", "Letter Spacing", "letterSpacing", value = 1.0)
        self.newInput("Float", "Word Spacing", "wordSpacing", value = 1.0)
        self.newInput("Float", "Line Spacing", "lineSpacing", value = 1.0)

        self.newInput("Float", "X Offset", "xOffset")
        self.newInput("Float", "Y Offset", "yOffset")
        self.newInput("Text", "Align", "align", value = "CENTER")

        self.newInput("Font", "Font", "font")
        self.newInput("Font", "Bold Font", "fontBold")
        self.newInput("Font", "Italic Font", "fontItalic")
        self.newInput("Font", "Bold Italic Font", "fontBoldItalic")

        for socket in self.inputs[1:]:
            socket.useIsUsedProperty = True
            socket.isUsed = False
        for socket in self.inputs[4:]:
            socket.hide = True

        self.newOutput("Object", "Object", "object")

    def draw(self, layout):
        if self.errorMessage != "":
            writeText(layout, self.errorMessage, width = 25, icon = "ERROR")

    def drawAdvanced(self, layout):
        writeText(layout, "Possible values for 'Align' are 'LEFT', 'CENTER', 'RIGHT', 'JUSTIFY' and 'FLUSH'")

    def getExecutionCode(self):
        yield "if getattr(object, 'type', '') == 'FONT':"
        yield "    textObject = object.data"

        s = self.inputs
        if s["Text"].isUsed:                yield "    if str(textObject.body) != text: textObject.body = text"
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
            if bpy.data.version < (2, 78, 0):
                textObject.align = align
            else:
                textObject.align_x = align
            self.errorMessage = ""
        else:
            self.errorMessage = "The align type is invalid. Look in the advanced panels to see all possible values."

    def getBakeCode(self):
        yield "if getattr(object, 'type', '') == 'FONT':"
        yield "    textObject = object.data"

        s = self.inputs
        if s["Size"].isUsed:                yield "    textObject.keyframe_insert('size')"
        if s["Extrude"].isUsed:             yield "    textObject.keyframe_insert('extrude')"
        if s["Shear"].isUsed:               yield "    textObject.keyframe_insert('shear')"
        if s["Bevel Depth"].isUsed:         yield "    textObject.keyframe_insert('bevel_depth')"
        if s["Bevel Resolution"].isUsed:    yield "    textObject.keyframe_insert('bevel_resolution')"

        if s["Letter Spacing"].isUsed:      yield "    textObject.keyframe_insert('space_character')"
        if s["Word Spacing"].isUsed:        yield "    textObject.keyframe_insert('space_word')"
        if s["Line Spacing"].isUsed:        yield "    textObject.keyframe_insert('space_line')"

        if s["X Offset"].isUsed:            yield "    textObject.keyframe_insert('offset_x')"
        if s["Y Offset"].isUsed:            yield "    textObject.keyframe_insert('offset_y')"
        if s["Align"].isUsed:               yield "    textObject.keyframe_insert('align')"
