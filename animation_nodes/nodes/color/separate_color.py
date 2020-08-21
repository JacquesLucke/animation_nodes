import bpy, colorsys
from bpy.props import *
from ... base_types import AnimationNode, VectorizedSocket

# using linear conversion here, unlike BL colorpicker hsv/hex
# BL Color() funcion does this also and has only rgb+hsv, so we'l use colorsys
# only hsv/hex in the colorpicker are gamma corrected for colorspaces
# we shall not use other functions, till they are in context (BL color space)

targetTypeItems = [
    ("RGB", "RGB", "Red, Green, Blue"),
    ("HSV", "HSV", "Hue, Saturation, Value"),
    ("HSL", "HSL", "Hue, Saturation, Lightness"),
    ("YIQ", "YIQ", "Luma, Chrominance")]

class SeparateColorNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_SeparateColorNode"
    bl_label = "Separate Color"
    dynamicLabelType = "HIDDEN_ONLY"

    useList: VectorizedSocket.newProperty()

    targetType: EnumProperty(name = "Target Type", items = targetTypeItems,
        default = "RGB", update = AnimationNode.refresh)

    def create(self):
        self.newInput(VectorizedSocket("Color", "useList", ("Color", "color"), ("Colors", "colors")))

        if self.targetType == "RGB":
            self.newOutput(VectorizedSocket("Float", "useList", ("R", "r"), ("R", "r")))
            self.newOutput(VectorizedSocket("Float", "useList", ("G", "g"), ("G", "g")))
            self.newOutput(VectorizedSocket("Float", "useList", ("B", "b"), ("B", "b")))
        elif self.targetType == "HSV":
            self.newOutput(VectorizedSocket("Float", "useList", ("H", "h"), ("H", "h")))
            self.newOutput(VectorizedSocket("Float", "useList", ("S", "s"), ("S", "s")))
            self.newOutput(VectorizedSocket("Float", "useList", ("V", "v"), ("V", "v")))
        elif self.targetType == "HSL":
            self.newOutput(VectorizedSocket("Float", "useList", ("H", "h"), ("H", "h")))
            self.newOutput(VectorizedSocket("Float", "useList", ("S", "s"), ("S", "s")))
            self.newOutput(VectorizedSocket("Float", "useList", ("L", "l"), ("L", "l")))
        elif self.targetType == "YIQ":
            self.newOutput(VectorizedSocket("Float", "useList", ("Y", "y"), ("Y", "y")))
            self.newOutput(VectorizedSocket("Float", "useList", ("I", "i"), ("I", "i")))
            self.newOutput(VectorizedSocket("Float", "useList", ("Q", "q"), ("Q", "q")))

    def draw(self, layout):
        layout.prop(self, "targetType", expand = True)

    def drawLabel(self):
        return "{}A from Color".format(self.targetType)

    def drawAdvanced(self, layout):
        layout.label(text = "Uses linear color space", icon = "INFO")

    def getExecutionCode(self, required):
        if self.useList:
            if self.targetType == "RGB":    yield "r, g, b, a = AN.nodes.color.c_utils.RGBAFromColorList(colors)"
            elif self.targetType == "HSV":  yield "h, s, v, a = AN.nodes.color.c_utils.HSVAFromColorList(colors)"
            elif self.targetType == "HSL":  yield "h, s, l, a = AN.nodes.color.c_utils.HSLAFromColorList(colors)"
            elif self.targetType == "YIQ":  yield "y, i, q, a = AN.nodes.color.c_utils.YIQAFromColorList(colors)"
        else:
            if self.targetType == "RGB":    yield "r, g, b = color.r, color.g, color.b"
            elif self.targetType == "HSV":  yield "h, s, v = colorsys.rgb_to_hsv(color.r, color.g, color.b)"
            elif self.targetType == "HSL":  yield "h, l, s = colorsys.rgb_to_hls(color.r, color.g, color.b)"
            elif self.targetType == "YIQ":  yield "y, i, q = colorsys.rgb_to_yiq(color.r, color.g, color.b)"
            yield "a = color.a"

    def getUsedModules(self):
        return ["colorsys"]
