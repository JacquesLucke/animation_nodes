import bpy
from bpy.props import *
from ... events import executionCodeChanged
from ... base_types.node import AnimationNode
from ... algorithms.interpolation import (linear,
                                          sinInOut, sinIn, sinOut,
                                          backInOut, backIn, backOut,
                                          powerInOut, powerIn, powerOut,
                                          circularInOut, circularIn, circularOut,
                                          prepareBounceSettings, bounceInOut, bounceIn, bounceOut,
                                          prepareElasticSettings, elasticInOut, elasticIn, elasticOut,
                                          prepareExponentialSettings, exponentialInOut, exponentialIn, exponentialOut)

categoryItems = [
    ("LINEAR", "Linear", "", "IPO_LINEAR", 0),
    ("SINUSOIDAL", "Sinusoidal", "", "IPO_SINE", 1),
    ("POWER", "Power", "", "IPO_QUAD", 2),
    ("EXPONENTIAL", "Exponential", "", "IPO_EXPO", 3),
    ("CIRCULAR", "Circular", "", "IPO_CIRC", 4),
    ("BACK", "Back", "", "IPO_BACK", 5),
    ("BOUNCE", "Bounce", "", "IPO_BOUNCE", 6),
    ("ELASTIC", "Elastic", "", "IPO_ELASTIC", 7)]

class ConstructInterpolationNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_ConstructInterpolationNode"
    bl_label = "Construct Interpolation"

    def categoryChanged(self, context = None):
        self.inputs[0].hide = self.category not in ("POWER", "EXPONENTIAL")
        self.inputs[1].hide = self.category not in ("EXPONENTIAL", "ELASTIC")
        self.inputs[2].hide = self.category not in ("BACK", "BOUNCE")
        self.inputs[3].hide = self.category not in ("ELASTIC", )
        self.inputs[4].hide = self.category not in ("BOUNCE", "ELASTIC")
        executionCodeChanged()

    category = EnumProperty(name = "Category", default = "LINEAR",
        items = categoryItems, update = categoryChanged)

    easeIn = BoolProperty(name = "Ease In", default = False, update = categoryChanged)
    easeOut = BoolProperty(name = "Ease Out", default = True, update = categoryChanged)

    def create(self):
        self.width = 160

        socket = self.inputs.new("an_IntegerSocket", "Exponent", "intExponent")
        socket.value = 2
        socket.minValue = 1

        socket = self.inputs.new("an_FloatSocket", "Base", "floatBase")
        socket.value = 2
        socket.minValue = 0.001

        socket = self.inputs.new("an_FloatSocket", "Size", "floatSize")
        socket.value = 1.4

        socket = self.inputs.new("an_FloatSocket", "Exponent", "floatExponent")
        socket.value = 2

        socket = self.inputs.new("an_IntegerSocket", "Bounces", "intBounces")
        socket.value = 4
        socket.minValue = 1


        self.outputs.new("an_InterpolationSocket", "Interpolation", "interpolation")
        self.categoryChanged()

    def draw(self, layout):
        row = layout.row(align = True)
        row.prop(self, "category", text = "")
        if self.category != "LINEAR":
            row.prop(self, "easeIn", text = "", icon = "IPO_EASE_IN")
            row.prop(self, "easeOut", text = "", icon = "IPO_EASE_OUT")

    def getExecutionCode(self):
        c = self.category
        if not (self.easeIn or self.easeOut): return "interpolation = self.getLinear()"
        if c == "LINEAR": return "interpolation = self.getLinear()"
        if c == "SINUSOIDAL": return "interpolation = self.getSinusoidal()"
        if c == "POWER": return "interpolation = self.getPower(intExponent)"
        if c == "EXPONENTIAL": return "interpolation = self.getExponential(floatBase, intExponent)"
        if c == "CIRCULAR": return "interpolation = self.getCircular()"
        if c == "BACK": return "interpolation = self.getBack(floatSize)"
        if c == "BOUNCE": return "interpolation = self.getBounce(intBounces, floatSize)"
        if c == "ELASTIC": return "interpolation = self.getElastic(floatBase, floatExponent, intBounces)"

    def getLinear(self):
        return (linear, None)

    def getSinusoidal(self):
        if self.easeIn and self.easeOut: return (sinInOut, None)
        if self.easeIn: return (sinIn, None)
        return (sinOut, None)

    def getPower(self, exponent):
        exponent = max(0, int(exponent))
        if self.easeIn and self.easeOut: return (powerInOut, exponent)
        if self.easeIn: return (powerIn, exponent)
        return (powerOut, exponent)

    def getExponential(self, base, exponent):
        settings = prepareExponentialSettings(base, exponent)
        if self.easeIn and self.easeOut: return (exponentialInOut, settings)
        if self.easeIn: return (exponentialIn, settings)
        return (exponentialOut, settings)

    def getCircular(self):
        if self.easeIn and self.easeOut: return (circularInOut, None)
        if self.easeIn: return (circularIn, None)
        return (circularOut, None)

    def getBack(self, back):
        if self.easeIn and self.easeOut: return (backInOut, back)
        if self.easeIn: return (backIn, back)
        return (backOut, back)

    def getBounce(self, bounces, base):
        settings = prepareBounceSettings(bounces, base)
        if self.easeIn and self.easeOut: return (bounceInOut, settings)
        if self.easeIn: return (bounceIn, settings)
        return (bounceOut, settings)

    def getElastic(self, base, exponent, bounces):
        settings = prepareElasticSettings(base, exponent, bounces)
        if self.easeIn and self.easeOut: return (elasticInOut, settings)
        if self.easeIn: return (elasticIn, settings)
        return (elasticOut, settings)
