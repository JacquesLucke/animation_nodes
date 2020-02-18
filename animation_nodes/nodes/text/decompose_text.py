import bpy
import blf
from bpy.props import *
from mathutils import Matrix
from string import whitespace
from functools import lru_cache
from ... events import propertyChanged
from ... base_types import AnimationNode, VectorizedSocket
from ... data_structures import Matrix4x4List, VirtualDoubleList, VirtualPyList

class DecomposeTextNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_DecomposeTextNode"
    bl_label = "Decompose Text"
    errorHandlingType = "EXCEPTION"

    useSizeList : VectorizedSocket.newProperty()
    useCharSpacingList : VectorizedSocket.newProperty()
    useWordSpacingList : VectorizedSocket.newProperty()
    useLineSpacingList : VectorizedSocket.newProperty()
    useAlignmentList : VectorizedSocket.newProperty()

    includeWhiteSpaces : BoolProperty(name = "Include White Spaces", default = True,
        update = propertyChanged)

    def create(self):
        self.newInput("Text", "Text", "text")
        self.newInput("Font", "Font", "font")
        self.newInput(VectorizedSocket("Float", "useSizeList",
            ("Size", "size", dict(value = 1, hide = True)),
            ("Sizes", "sizes")))
        self.newInput(VectorizedSocket("Float", "useCharSpacingList",
            ("Character Spacing", "charSpacing", dict(value = 1, hide = True)),
            ("Characters Spacing", "charsSpacing")))
        self.newInput(VectorizedSocket("Float", "useWordSpacingList",
            ("Word Spacing", "wordSpacing", dict(value = 1, hide = True)),
            ("Words Spacing", "wordsSpacing")))
        self.newInput(VectorizedSocket("Float", "useLineSpacingList",
            ("Line Spacing", "lineSpacing", dict(value = 1, hide = True)),
            ("Lines Spacing", "linesSpacing")))
        self.newInput(VectorizedSocket("Text", "useAlignmentList",
            ("Alignment", "alignment", dict(value = "LEFT", hide = True)),
            ("Alignments", "alignments")))

        self.newOutput("Matrix List", "Transforms", "transforms")
        self.newOutput("Text List", "Characters", "characters")
        self.newOutput("Integer", "Length", "length")

    def drawAdvanced(self, layout):
        layout.prop(self, "includeWhiteSpaces")

    def execute(self, text, font, sizes, charsSpacing, wordsSpacing, linesSpacing, alignments):
        self.validateAlignments(alignments)
        fontID = self.getFontID(font)
        fontRatio = getFontRatio(font, fontID)

        sizes, charsSpacing, wordsSpacing, linesSpacing = VirtualDoubleList.createMultiple(
                (sizes, 1), (charsSpacing, 1), (wordsSpacing, 1), (linesSpacing, 1))
        alignments = VirtualPyList.create(alignments, "LEFT")

        return self.getCharTransforms(text, fontID, fontRatio, sizes,
            charsSpacing, wordsSpacing, linesSpacing, alignments)

    def getCharTransforms(self, text, fontID, fontRatio, sizes,
            charsSpacing, wordsSpacing, linesSpacing, alignments):
        allChars = []
        allTransforms = Matrix4x4List()
        for i, line in enumerate(text.splitlines()):
            chars = []
            transforms = []
            numberOfSpaces = 0
            cumulativeWidth = 0
            for j, char in enumerate(line):
                if self.includeWhiteSpaces or char not in whitespace:
                    scale = Matrix.Scale(sizes[j], 4)
                    translation = Matrix.Translation((cumulativeWidth, -i * linesSpacing[i], 0))
                    transforms.append(translation @ scale)
                    chars.append(char)
                
                cumulativeWidth += getCharWidth(fontID, char, fontRatio,
                    charsSpacing[j], wordsSpacing[numberOfSpaces]) * sizes[j]

                if char == " ": numberOfSpaces += 1

            transforms = Matrix4x4List.fromValues(transforms)

            if alignments[i] != "LEFT":
                lastCharIndex = len(line) - 1
                spacing, size = charsSpacing[lastCharIndex], sizes[lastCharIndex]
                offset = -cumulativeWidth + (spacing / 2 - 0.5) * size
                if alignments[i] == "CENTER": offset /= 2
                transforms.transform(Matrix.Translation((offset, 0, 0)))

            allChars += chars
            allTransforms.extend(transforms)

        return allTransforms, allChars, len(allChars)


    def getFontID(self, font):
        if font is None or font.filepath == "<builtin>":
            self.raiseErrorMessage("BFont is not supported!")

        fontID = blf.load(font.filepath)

        if fontID == -1:
            self.raiseErrorMessage("Can't load font!")

        blf.size(fontID, 50, 72)
        return fontID

    def validateAlignments(self, alignments):
        if not self.useAlignmentList:
            alignments = [alignments]

        for alignment in alignments:
            if alignment not in ("LEFT", "RIGHT", "CENTER"):
                self.raiseErrorMessage("Invalid alignment. Possible values are 'LEFT', 'CENTER', and 'RIGHT'.")


def getCharWidth(fontID, char, fontRatio, charSpacing, wordSpacing):
    width = blf.dimensions(fontID, char)[0] * fontRatio
    if char == " ":
        width *= wordSpacing
    return width + charSpacing / 2 - 0.5

@lru_cache()
def getFontRatio(font, fontID):
    data = bpy.data.curves.new("an_helper_font_curve", type = "FONT")
    textObject = bpy.data.objects.new("an_helper_text_object", data)

    referenceChar = "W"

    data.font = font
    data.body = referenceChar
    data.body_format[0].use_underline = True

    actualWidth = textObject.dimensions[0]
    blfWidth = blf.dimensions(fontID, referenceChar)[0]

    # textObject will be removed automatically.
    bpy.data.curves.remove(data)

    return actualWidth / blfWidth

