import bpy
import blf
from bpy.props import *
from mathutils import Matrix
from string import whitespace
from functools import lru_cache
from ... events import propertyChanged
from ... base_types import AnimationNode, VectorizedSocket
from ... data_structures import Matrix4x4List, VirtualDoubleList

class DecomposeTextNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_DecomposeTextNode"
    bl_label = "Decompose Text"
    errorHandlingType = "EXCEPTION"

    useScaleList : VectorizedSocket.newProperty()

    includeWhiteSpaces : BoolProperty(name = "Include White Spaces", default = True,
        update = propertyChanged)

    def create(self):
        self.newInput("Text", "Text", "text")
        self.newInput("Font", "Font", "font")
        self.newInput(VectorizedSocket("Float", "useScaleList",
            ("Size", "size", dict(value = 1, hide = True)),
            ("Sizes", "sizes")))
        self.newInput("Float", "Character Spacing", "charSpacing", value = 1, hide = True)
        self.newInput("Float", "Word Spacing", "wordSpacing", value = 1, hide = True)
        self.newInput("Float", "Line Spacing", "lineSpacing", value = 1, hide = True)
        self.newInput("Text", "Alignment", "align", value = "LEFT", hide = True)

        self.newOutput("Matrix List", "Transforms", "transforms")
        self.newOutput("Text List", "Characters", "characters")
        self.newOutput("Integer", "Length", "length")

    def drawAdvanced(self, layout):
        layout.prop(self, "includeWhiteSpaces")

    def execute(self, text, font, sizes, charSpacing, wordSpacing, lineSpacing, align):
        self.validateAlignment(align)
        fontID = self.getFontID(font)
        fontRatio = getFontRatio(font, fontID)

        return self.getCharTransforms(text, fontID, fontRatio, sizes, charSpacing, wordSpacing, lineSpacing, align)

    def getCharTransforms(self, text, fontID, fontRatio, sizes, charSpacing, wordSpacing, lineSpacing, align):
        _sizes = VirtualDoubleList.create(sizes, 1)

        allChars = []
        allTransforms = Matrix4x4List()
        for i, line in enumerate(text.splitlines()):
            chars = []
            transforms = []
            cumulativeWidth = 0
            for j, char in enumerate(line):
                if self.includeWhiteSpaces or char not in whitespace:
                    scale = Matrix.Scale(_sizes[j], 4)
                    translation = Matrix.Translation((cumulativeWidth, -i * lineSpacing, 0))
                    transforms.append(translation @ scale)
                    chars.append(char)

                cumulativeWidth += getCharWidth(fontID, char, fontRatio, charSpacing, wordSpacing) * _sizes[j]

            transforms = Matrix4x4List.fromValues(transforms)

            if align == "CENTER":
                offset = (-cumulativeWidth + (charSpacing / 2 - 0.5) * _sizes[len(line) - 1]) / 2
                transforms.transform(Matrix.Translation((offset, 0, 0)))
            elif align == "RIGHT":
                offset = -cumulativeWidth + (charSpacing / 2 - 0.5) * _sizes[len(line) - 1]
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

    def validateAlignment(self, align):
        if align not in ("LEFT", "RIGHT", "CENTER"):
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

