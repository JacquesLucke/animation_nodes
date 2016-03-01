import bpy, colorsys
from bpy.props import *
from ... events import executionCodeChanged
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
    
    def targetTypeChanged(self, context):
        self.updateHideStatus()
        executionCodeChanged()
        
    targetType = EnumProperty(name = "Target Type", items = targetTypeItems,
                                    default = "RGB", update = targetTypeChanged)

    def create(self):
        self.inputs.new("an_ColorSocket", "Color", "color")
        
        self.outputs.new("an_FloatSocket", "Red", "r")
        self.outputs.new("an_FloatSocket", "Green", "g")
        self.outputs.new("an_FloatSocket", "Blue", "b")
        
        self.outputs.new("an_FloatSocket", "Hue", "h")
        self.outputs.new("an_FloatSocket", "Saturation", "s")
        self.outputs.new("an_FloatSocket", "Value", "v")
        
        #same H, S (attention HLS/HSL order! using HSL for sockets, but function does hls)
        self.outputs.new("an_FloatSocket", "Lightness", "l")
        
        self.outputs.new("an_FloatSocket", "Y Luma", "y")
        self.outputs.new("an_FloatSocket", "I In phase", "i")
        self.outputs.new("an_FloatSocket", "Q Quadrature", "q")
        
        self.outputs.new("an_FloatSocket", "Alpha", "alpha")
        self.updateHideStatus()
        
    def draw(self, layout):
        layout.prop(self, "targetType", expand = True)
        
    def drawLabel(self):
        return "--> " + self.targetType + "a (Linear)"
    
    def getExecutionCode(self):
        yield "r = g = b = h = s = v = l = y = i = q = 0"
        if self.targetType == "RGB":    yield "r, g, b = color[0], color[1], color[2]"
        elif self.targetType == "HSV":  yield "h, s, v = colorsys.rgb_to_hsv(color[0], color[1], color[2])"
        elif self.targetType == "HSL":  yield "h, l, s = colorsys.rgb_to_hls(color[0], color[1], color[2])"#attention to the HLS order!
        elif self.targetType == "YIQ":  yield "y, i, q = colorsys.rgb_to_yiq(color[0], color[1], color[2])"
        yield "alpha = color[3]"
    
    def getUsedModules(self):
        return ["colorsys"]

    def updateHideStatus(self):
        for socket in self.outputs[:-1]: socket.hide = True

        if self.targetType == "RGB":
            self.outputs["Red"].hide = False
            self.outputs["Green"].hide = False
            self.outputs["Blue"].hide = False
        elif self.targetType == "HSV":
            self.outputs["Hue"].hide = False
            self.outputs["Saturation"].hide = False
            self.outputs["Value"].hide = False
        elif self.targetType == "HSL":
            self.outputs["Hue"].hide = False
            self.outputs["Saturation"].hide = False
            self.outputs["Lightness"].hide = False
        elif self.targetType == "YIQ":
            self.outputs["Y Luma"].hide = False
            self.outputs["I In phase"].hide = False
            self.outputs["Q Quadrature"].hide = False
