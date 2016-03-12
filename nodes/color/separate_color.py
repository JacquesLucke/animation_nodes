import bpy, colorsys
from bpy.props import *
from ... tree_info import keepNodeState
from ... base_types.node import AnimationNode

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

    def targetTypeChanged(self, context):
        self.recreateOutputs()

    targetType = EnumProperty(name = "Target Type", items = targetTypeItems,
                                    default = "RGB", update = targetTypeChanged)

    def create(self):
        self.inputs.new("an_ColorSocket", "Color", "color")
        self.recreateOutputs()

    @keepNodeState
    def recreateOutputs(self):
        self.outputs.clear()

        if self.targetType == "RGB":
            self.outputs.new("an_FloatSocket", "Red", "r")
            self.outputs.new("an_FloatSocket", "Green", "g")
            self.outputs.new("an_FloatSocket", "Blue", "b")
        elif self.targetType == "HSV":
            self.outputs.new("an_FloatSocket", "Hue", "h")
            self.outputs.new("an_FloatSocket", "Saturation", "s")
            self.outputs.new("an_FloatSocket", "Value", "v")
        elif self.targetType == "HSL":
            self.outputs.new("an_FloatSocket", "Hue", "h")
            self.outputs.new("an_FloatSocket", "Saturation", "s")
            self.outputs.new("an_FloatSocket", "Lightness", "l")
        elif self.targetType == "YIQ":
            self.outputs.new("an_FloatSocket", "Y Luma", "y")
            self.outputs.new("an_FloatSocket", "I In phase", "i")
            self.outputs.new("an_FloatSocket", "Q Quadrature", "q")

        self.outputs.new("an_FloatSocket", "Alpha", "alpha")

    def draw(self, layout):
        layout.prop(self, "targetType", expand = True)

    def drawLabel(self):
        return "{}a from Color".format(self.targetType)

    def getExecutionCode(self):
        if self.targetType == "RGB":    yield "r, g, b = color[0], color[1], color[2]"
        elif self.targetType == "HSV":  yield "h, s, v = colorsys.rgb_to_hsv(color[0], color[1], color[2])"
        elif self.targetType == "HSL":  yield "h, l, s = colorsys.rgb_to_hls(color[0], color[1], color[2])"
        elif self.targetType == "YIQ":  yield "y, i, q = colorsys.rgb_to_yiq(color[0], color[1], color[2])"
        yield "alpha = color[3]"

    def getUsedModules(self):
        return ["colorsys"]
