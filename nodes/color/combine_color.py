import bpy, colorsys
from bpy.props import *
from ... events import executionCodeChanged
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
    
    def sourceTypeChanged(self, context):
        self.updateHideStatus()
        executionCodeChanged()
    
    sourceType = EnumProperty(name = "Source Type", items = sourceTypeItems, 
                                    default = "RGB", update = sourceTypeChanged)

    def create(self):
        self.inputs.new("an_FloatSocket", "Red", "red")
        self.inputs.new("an_FloatSocket", "Green", "green")
        self.inputs.new("an_FloatSocket", "Blue", "blue")
        
        self.inputs.new("an_FloatSocket", "Hue", "hue")
        self.inputs.new("an_FloatSocket", "Saturation", "saturation")
        self.inputs.new("an_FloatSocket", "Value", "value")
        
        #same H, S (attention HLS/HSL order! using HSL for sockets, but function does hls!)
        self.inputs.new("an_FloatSocket", "Lightness", "lightness")
        
        self.inputs.new("an_FloatSocket", "Y Luma", "y")
        self.inputs.new("an_FloatSocket", "I In phase", "i")
        self.inputs.new("an_FloatSocket", "Q Quadrature", "q")
        
        self.inputs.new("an_FloatSocket", "Alpha", "alpha").value = 1
        self.updateHideStatus()
        self.outputs.new("an_ColorSocket", "Color", "color")
        
    def draw(self, layout):
        layout.prop(self, "sourceType", expand = True)
        
    def drawLabel(self):
        return self.sourceType + "a --> Col (Linear)"

    def getExecutionCode(self):
        if self.sourceType == "RGB":    yield "C = [red, green, blue]"
        elif self.sourceType == "HSV":  yield "C = colorsys.hsv_to_rgb(hue, saturation, value)"
        elif self.sourceType == "HSL":  yield "C = colorsys.hls_to_rgb(hue, lightness, saturation)"
        elif self.sourceType == "YIQ":  yield "C = colorsys.yiq_to_rgb(y, i, q)"
        yield "color = [C[0], C[1], C[2], alpha]"
    
    def getUsedModules(self):
        return ["colorsys"]

    def updateHideStatus(self):
        for socket in self.inputs[:-1]: socket.hide = True

        if self.sourceType == "RGB":
            self.inputs["Red"].hide = False
            self.inputs["Green"].hide = False
            self.inputs["Blue"].hide = False
        elif self.sourceType == "HSV":
            self.inputs["Hue"].hide = False
            self.inputs["Saturation"].hide = False
            self.inputs["Value"].hide = False
        elif self.sourceType == "HSL":
            self.inputs["Hue"].hide = False
            self.inputs["Saturation"].hide = False
            self.inputs["Lightness"].hide = False
        elif self.sourceType == "YIQ":
            self.inputs["Y Luma"].hide = False
            self.inputs["I In phase"].hide = False
            self.inputs["Q Quadrature"].hide = False
