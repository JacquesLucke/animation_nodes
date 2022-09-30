import bpy, colorsys
from bpy.props import *
from ... data_structures import VirtualDoubleList
from ... base_types import AnimationNode, VectorizedSocket
from . c_utils import (
    colorListFromRGBA,
    colorListFromHSVA,
    colorListFromHSLA,
    colorListFromYIQA,
)


# using linear conversion here, unlike BL colorpicker hsv/hex
# BL Color() funcion does this also and has only rgb+hsv, so we'l use colorsys
# only hsv/hex in the colorpicker are gamma corrected for colorspaces
# we shall not use other functions, till they are in context (BL color space)

sourceTypeItems = [
    ("RGB", "RGB", "Red, Green, Blue"),
    ("HSV", "HSV", "Hue, Saturation, Value"),
    ("HSL", "HSL", "Hue, Saturation, Lightness"),
    ("YIQ", "YIQ", "Luma, Chrominance")]

class CombineColorNode(AnimationNode, bpy.types.Node):
    bl_idname = "an_CombineColorNode"
    bl_label = "Combine Color"
    dynamicLabelType = "HIDDEN_ONLY"

    useListR: VectorizedSocket.newProperty()
    useListG: VectorizedSocket.newProperty()
    useListB: VectorizedSocket.newProperty()
    useListA: VectorizedSocket.newProperty()

    sourceType: EnumProperty(name = "Source Type", default = "RGB",
        items = sourceTypeItems, update = AnimationNode.refresh)

    def create(self):
        if self.sourceType == "RGB":
            self.newInput(VectorizedSocket("Float", "useListR", ("R", "r"), ("R", "r")))
            self.newInput(VectorizedSocket("Float", "useListG", ("G", "g"), ("G", "g")))
            self.newInput(VectorizedSocket("Float", "useListB", ("B", "b"), ("B", "b")))
        elif self.sourceType == "HSV":
            self.newInput(VectorizedSocket("Float", "useListR", ("H", "h"), ("H", "h")))
            self.newInput(VectorizedSocket("Float", "useListG", ("S", "s"), ("S", "s")))
            self.newInput(VectorizedSocket("Float", "useListB", ("V", "v"), ("V", "v")))
        elif self.sourceType == "HSL":
            self.newInput(VectorizedSocket("Float", "useListR", ("H", "h"), ("H", "h")))
            self.newInput(VectorizedSocket("Float", "useListG", ("S", "s"), ("S", "s")))
            self.newInput(VectorizedSocket("Float", "useListB", ("L", "l"), ("L", "l")))
        elif self.sourceType == "YIQ":
            self.newInput(VectorizedSocket("Float", "useListR", ("Y", "y"), ("Y", "y")))
            self.newInput(VectorizedSocket("Float", "useListG", ("I", "i"), ("I", "i")))
            self.newInput(VectorizedSocket("Float", "useListB", ("Q", "q"), ("Q", "q")))

        self.newInput(VectorizedSocket("Float", "useListA", ("A", "a"), ("A", "a")))

        self.newOutput(VectorizedSocket("Color",
            ["useListR", "useListG", "useListB", "useListA"],
            ("Color", "color"), ("Colors", "colors")))

    def draw(self, layout):
        layout.prop(self, "sourceType", expand = True)

    def drawAdvanced(self, layout):
        layout.label(text = "Uses linear color space", icon = "INFO")

    def drawLabel(self):
        return "Color from {}A".format(self.sourceType)

    def getExecutionCode(self, required):
        if any((self.useListR, self.useListG, self.useListB, self.useListA)):
            if self.sourceType == "RGB": yield "colors = self.createColorList(r, g, b, a)"
            elif self.sourceType == "HSV": yield "colors = self.createColorList(h, s, v, a)"
            elif self.sourceType == "HSL": yield "colors = self.createColorList(h, s, l, a)"
            elif self.sourceType == "YIQ": yield "colors = self.createColorList(y, i, q, a)"
        else:
            if self.sourceType == "RGB":    yield "color = Color((r, g, b, a))"
            elif self.sourceType == "HSV":  yield "color = Color((*colorsys.hsv_to_rgb(h, s, v), a))"
            elif self.sourceType == "HSL":  yield "color = Color((*colorsys.hls_to_rgb(h, l, s), a))"
            elif self.sourceType == "YIQ":  yield "color = Color((*colorsys.yiq_to_rgb(y, i, q), a))"

    def createColorList(self, r, g, b, a):
        r, g, b, a = VirtualDoubleList.createMultiple((r, 0), (g, 0), (b, 0), (a, 0))
        amount = VirtualDoubleList.getMaxRealLength(r, g, b, a)
        if self.sourceType == "RGB":
            return colorListFromRGBA(amount, r, g, b, a)
        if self.sourceType == "HSV":
            return colorListFromHSVA(amount, r, g, b, a)
        if self.sourceType == "HSL":
            return colorListFromHSLA(amount, r, g, b, a)
        if self.sourceType == "YIQ":
            return colorListFromYIQA(amount, r, g, b, a)

    def getUsedModules(self):
        return ["colorsys"]
