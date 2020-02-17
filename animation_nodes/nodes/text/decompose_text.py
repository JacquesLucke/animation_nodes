import bpy
import blf
from bpy.props import *
from mathutils import Matrix
from string import whitespace
from functools import lru_cache
from ... events import propertyChanged
from ... data_structures import Matrix4x4List
from ... base_types import AnimationNode, VectorizedSocket

class DecomposeTextNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_DecomposeTextNode"
    bl_label = "Decompose Text"
    errorHandlingType = "EXCEPTION"

    includeWhiteSpaces : BoolProperty(name = "Include White Spaces", default = True,
        update = propertyChanged)

    def create(self):
        self.newInput("Text", "Text", "text")
        self.newInput("Font", "Font", "font")
        self.newInput("Float", "Character Spacing", "charSpacing", value = 1, hide = True)
        self.newInput("Float", "Word Spacing", "wordSpacing", value = 1, hide = True)
        self.newInput("Float", "Line Spacing", "lineSpacing", value = 1, hide = True)
        self.newInput("Text", "Alignment", "align", value = "LEFT", hide = True)

        self.newOutput("Matrix List", "Transforms", "transforms")
        self.newOutput("Text List", "Characters", "characters")
        self.newOutput("Integer", "Length", "length")

    def drawAdvanced(self, layout):
        layout.prop(self, "includeWhiteSpaces")

    def execute(self, text, font, charSpacing, wordSpacing, lineSpacing, align):
        self.validateAlignment(align)
        fontID = self.getFontID(font)
        fontRatio = self.getFontRatio(font, fontID)

        return self.getCharTransforms(text, fontID, fontRatio, charSpacing, wordSpacing, lineSpacing, align)

    def getCharTransforms(self, text, fontID, fontRatio, charSpacing, wordSpacing, lineSpacing, align):
        allChars = []
        allTransforms = Matrix4x4List()
        for i, line in enumerate(text.splitlines()):
            chars = []
            transforms = []
            comulativeWidth = 0
            for char in line:
                if self.includeWhiteSpaces or char not in whitespace:
                    transforms.append(Matrix.Translation((comulativeWidth, -i * lineSpacing, 0)))
                    chars.append(char)

                comulativeWidth += self.getCharWidth(fontID, char, fontRatio, charSpacing, wordSpacing)

            transforms = Matrix4x4List.fromValues(transforms)

            if align == "CENTER":
                offset = (-comulativeWidth + charSpacing / 2 - 0.5) / 2
                transforms.transform(Matrix.Translation((offset, 0, 0)))
            elif align == "RIGHT":
                offset = -comulativeWidth + charSpacing / 2 - 0.5
                transforms.transform(Matrix.Translation((offset, 0, 0)))

            allChars += chars
            allTransforms.extend(transforms)

        return allTransforms, allChars, len(allChars)

    def getCharWidth(self, fontID, char, fontRatio, charSpacing, wordSpacing):
        width = blf.dimensions(fontID, char)[0] * fontRatio
        if char == " ":
            width *= wordSpacing
        return width + charSpacing / 2 - 0.5

    @lru_cache()
    def getFontRatio(self, font, fontID):
        data = bpy.data.curves.new("an_helper_font_curve", type = "FONT")
        textObject = bpy.data.objects.new("an_helper_text_object", data)

        referenceChar = "W"

        data.font = font
        data.body = referenceChar
        data.body_format[0].use_underline = True

        actualWidth = textObject.dimensions[0]
        blfWidth = blf.dimensions(fontID, referenceChar)[0]

        bpy.data.curves.remove(data)

        return actualWidth / blfWidth

    def getFontID(self, font):
        if font is None or font.filepath == "<builtin>":
            self.raiseErrorMessage("BFont is not supported!")

        fontID = blf.load(font.filepath)

        if fontID == -1:
            self.raiseErrorMessage("Can't load font!")

        blf.size(fontID, 50, 72)
        return fontID

    def validateAlignment(self, align):
        if align not in ("LEFT", "RIGHT", "CENTER"):
            self.raiseErrorMessage("Invalid alignment. Possible values are 'LEFT', 'CENTER', and 'RIGHT'.")
