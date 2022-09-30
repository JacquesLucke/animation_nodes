import re
import bpy
import blf
from bpy.props import *
from mathutils import Matrix
from string import whitespace
from functools import lru_cache
from ... events import propertyChanged
from ... base_types import AnimationNode, VectorizedSocket
from ... data_structures import Matrix4x4List, VirtualDoubleList, VirtualPyList

decomposeTypeItems = [
    ("CHARACTER", "Character", "", "NONE", 0),
    ("WORD", "Word", "", "NONE", 1),
]

class DecomposeTextNode(AnimationNode, bpy.types.Node):
    bl_idname = "an_DecomposeTextNode"
    bl_label = "Decompose Text"
    errorHandlingType = "EXCEPTION"

    useFontList : VectorizedSocket.newProperty()
    useSizeList : VectorizedSocket.newProperty()
    useCharSpacingList : VectorizedSocket.newProperty()
    useWordSpacingList : VectorizedSocket.newProperty()
    useLineSpacingList : VectorizedSocket.newProperty()
    useAlignmentList : VectorizedSocket.newProperty()

    decomposeType: EnumProperty(name = "Decompose Type", default = "CHARACTER",
        items = decomposeTypeItems, update = AnimationNode.refresh)

    def create(self):
        self.newInput("Text", "Text", "text")
        self.newInput(VectorizedSocket("Font", "useFontList",
            ("Font", "font"),
            ("Fonts", "fonts")))
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
        self.newInput("Boolean", "Include Whitespaces", "includeWhitespaces",
            value = True, hide = True)

        self.newOutput("Matrix List", "Transforms", "transforms")
        if self.decomposeType == "CHARACTER":
            self.newOutput("Text List", "Characters", "characters")
        else:
            self.newOutput("Text List", "Words", "words")
        self.newOutput("Integer", "Length", "length")

    def draw(self, layout):
        layout.prop(self, "decomposeType", text = "")

    def execute(self, text, fonts, sizes, charsSpacing, wordsSpacing, linesSpacing,
            alignments, includeWhitespaces):
        self.validateAlignments(alignments)
        if not self.useFontList: fonts = [fonts]
        fontIDs = [self.getFontID(font) for font in fonts]
        fontRatios = [getFontRatio(font, fontID) for font, fontID in zip(fonts, fontIDs)]

        sizes, charsSpacing, wordsSpacing, linesSpacing = VirtualDoubleList.createMultiple(
                (sizes, 1), (charsSpacing, 1), (wordsSpacing, 1), (linesSpacing, 1))
        fontIDs, fontRatios, alignments = VirtualPyList.createMultiple(
                (fontIDs, 0), (fontRatios, 1), (alignments, "LEFT"))

        if self.decomposeType == "CHARACTER":
            return self.getCharTransforms(text, fontIDs, fontRatios, sizes,
                charsSpacing, wordsSpacing, linesSpacing, alignments, includeWhitespaces)
        else:
            return self.getWordTransforms(text, fontIDs, fontRatios, sizes,
                charsSpacing, wordsSpacing, linesSpacing, alignments)

    def getCharTransforms(self, text, fontIDs, fontRatios, sizes,
            charsSpacing, wordsSpacing, linesSpacing, alignments, includeWhitespaces):
        allChars = []
        charIndex = 0
        spaceIndex = 0
        allTransforms = Matrix4x4List()
        for i, line in enumerate(text.splitlines()):
            chars = []
            transforms = []
            cumulativeWidth = 0
            for char in line:
                if includeWhitespaces or char not in whitespace:
                    scale = Matrix.Scale(sizes[charIndex], 4)
                    translation = Matrix.Translation((cumulativeWidth, -i * linesSpacing[i], 0))
                    transforms.append(translation @ scale)
                    chars.append(char)
                
                cumulativeWidth += getCharWidth(char, fontIDs[charIndex], fontRatios[charIndex],
                    charsSpacing[charIndex], wordsSpacing[spaceIndex]) * sizes[charIndex]

                charIndex += 1
                if char == " ": spaceIndex += 1

            transforms = Matrix4x4List.fromValues(transforms)

            if alignments[i] != "LEFT":
                spacing, size = charsSpacing[charIndex - 1], sizes[charIndex - 1]
                offset = -cumulativeWidth + (spacing / 2 - 0.5) * size
                if alignments[i] == "CENTER": offset /= 2
                transforms.transform(Matrix.Translation((offset, 0, 0)))

            allChars += chars
            allTransforms.extend(transforms)

        return allTransforms, allChars, len(allChars)

    def getWordTransforms(self, text, fontIDs, fontRatios, sizes,
            charsSpacing, wordsSpacing, linesSpacing, alignments):
        allWords = []
        wordIndex = 0
        spaceIndex = 0
        allTransforms = Matrix4x4List()
        for i, line in enumerate(text.splitlines()):
            words = []
            transforms = []
            cumulativeWidth = 0
            for word in re.split(r"(\s+)", line):
                isWord = len(word) != 0 and word[0] not in whitespace
                if isWord:
                    scale = Matrix.Scale(sizes[wordIndex], 4)
                    translation = Matrix.Translation((cumulativeWidth, -i * linesSpacing[i], 0))
                    transforms.append(translation @ scale)
                    words.append(word)

                cumulativeWidth += getWordWidth(word, fontIDs[wordIndex], fontRatios[wordIndex],
                    charsSpacing[wordIndex], wordsSpacing[spaceIndex]) * sizes[wordIndex]

                if isWord: wordIndex += 1
                else: spaceIndex += 1

            transforms = Matrix4x4List.fromValues(transforms)

            if alignments[i] != "LEFT":
                spacing, size = charsSpacing[wordIndex - 1], sizes[wordIndex - 1]
                offset = -cumulativeWidth + (spacing / 2 - 0.5) * size
                if alignments[i] == "CENTER": offset /= 2
                transforms.transform(Matrix.Translation((offset, 0, 0)))

            allWords += words
            allTransforms.extend(transforms)

        return allTransforms, allWords, len(allWords)

    def getFontID(self, font):
        if font is None or font.filepath == "<builtin>":
            self.raiseErrorMessage("BFont is not supported!")

        path = bpy.path.abspath(font.filepath, library = font.library)
        fontID = blf.load(path)

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


def getCharWidth(char, fontID, fontRatio, charSpacing, wordSpacing):
    width = blf.dimensions(fontID, char)[0] * fontRatio
    if char == " ":
        width *= wordSpacing
    return width + charSpacing / 2 - 0.5

def getWordWidth(word, fontID, fontRatio, charSpacing, wordSpacing):
    return sum(getCharWidth(char, fontID, fontRatio, charSpacing, wordSpacing) for char in word)

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

