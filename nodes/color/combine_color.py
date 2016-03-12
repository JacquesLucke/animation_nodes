import bpy, colorsys
from bpy.props import *
from ... tree_info import keepNodeState
from ... base_types.node import AnimationNode

# using linear conversion here, unlike BL colorpicker hsv/hex
# BL Color() funcion does this also and has only rgb+hsv, so we'l use colorsys
# only hsv/hex in the colorpicker are gamma corrected for colorspaces
# we shall not use other functions, till they are in context (BL color space)

sourceTypeItems = [
    ("RGB", "RGB", "Red, Green, Blue"),
    ("HSV", "HSV", "Hue, Saturation, Value"),
    ("HSL", "HSL", "Hue, Saturation, Lightness"),
    ("YIQ", "YIQ", "Luma, Chrominance")]

class CombineColorNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_CombineColorNode"
    bl_label = "Combine Color"
    dynamicLabelType = "HIDDEN_ONLY"

    def sourceTypeChanged(self, context):
        self.recreateInputs()

    sourceType = EnumProperty(name = "Source Type", default = "RGB",
        items = sourceTypeItems, update = sourceTypeChanged)

    def create(self):
        self.recreateInputs()
        self.outputs.new("an_ColorSocket", "Color", "color")

    @keepNodeState
    def recreateInputs(self):
        self.inputs.clear()

        if self.sourceType == "RGB":
            self.inputs.new("an_FloatSocket", "Red", "red")
            self.inputs.new("an_FloatSocket", "Green", "green")
            self.inputs.new("an_FloatSocket", "Blue", "blue")
        elif self.sourceType == "HSV":
            self.inputs.new("an_FloatSocket", "Hue", "hue")
            self.inputs.new("an_FloatSocket", "Saturation", "saturation")
            self.inputs.new("an_FloatSocket", "Value", "value")
        elif self.sourceType == "HSL":
            self.inputs.new("an_FloatSocket", "Hue", "hue")
            self.inputs.new("an_FloatSocket", "Saturation", "saturation")
            self.inputs.new("an_FloatSocket", "Lightness", "lightness")
        elif self.sourceType == "YIQ":
            self.inputs.new("an_FloatSocket", "Y Luma", "y")
            self.inputs.new("an_FloatSocket", "I In phase", "i")
            self.inputs.new("an_FloatSocket", "Q Quadrature", "q")

        self.inputs.new("an_FloatSocket", "Alpha", "alpha").value = 1

    def draw(self, layout):
        layout.prop(self, "sourceType", expand = True)

    def drawAdvanced(self, layout):
        layout.label("Uses linear color space", icon = "INFO")

    def drawLabel(self):
        return "Color from {}a".format(self.sourceType)

    def getExecutionCode(self):
        if self.sourceType == "RGB":    yield "color = [red, green, blue, alpha]"
        elif self.sourceType == "HSV":  yield "color = [*colorsys.hsv_to_rgb(hue, saturation, value), alpha]"
        elif self.sourceType == "HSL":  yield "color = [*colorsys.hls_to_rgb(hue, lightness, saturation), alpha]"
        elif self.sourceType == "YIQ":  yield "color = [*colorsys.yiq_to_rgb(y, i, q), alpha]"

    def getUsedModules(self):
        return ["colorsys"]
