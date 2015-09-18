import bpy, random, colorsys
from ... events import executionCodeChanged
from ... base_types.node import AnimationNode

#using linear conversion here, unlike BL colorpicker hsv/hex
#BL Color() funcion does this also and has only rgb+hsv, so we'l use colorsys
#only hsv/hex in the colorpicker are gamma corrected for colorspaces
#we shall not use other functions, till they are in context (BL color space)

targetTypeItems = [
    ("RGB", "RGB", "Red, Green, Blue"),            
    ("HSV", "HSV", "Hue, Saturation, Value"),      
    ("HSL", "HSL", "Hue, Saturation, Lightness"),  
    ("YIQ", "YIQ", "Luma, Chrominance")]           

class SeparateColorNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_SeparateColorNode"
    bl_label = "Separate Color"
    
    def targetTypeChanged(self, context):
        self.labelOperation = self.targetType
        self.updateHideStatus()
        executionCodeChanged()
        
    targetType = bpy.props.EnumProperty(name = "Target Type", items = targetTypeItems,
                                            default = "RGB", update = targetTypeChanged)
    labelOperation = bpy.props.StringProperty(name = "Operation Label", default = "RGB")
    
    def create(self):
        self.inputs.new("an_ColorSocket", "Color", "color")
        
        self.outputs.new("an_FloatSocket", "Red", "red")
        self.outputs.new("an_FloatSocket", "Green", "green")
        self.outputs.new("an_FloatSocket", "Blue", "blue")
        
        self.outputs.new("an_FloatSocket", "Hue", "hue")
        self.outputs.new("an_FloatSocket", "Saturation", "saturation")
        self.outputs.new("an_FloatSocket", "Value", "value")
        
        #same H, S (attention HLS/HSL order! using HSL for sockets, but function does hls)
        self.outputs.new("an_FloatSocket", "Lightness", "lightness")
        
        self.outputs.new("an_FloatSocket", "Y Luma", "y")
        self.outputs.new("an_FloatSocket", "I In phase", "i")
        self.outputs.new("an_FloatSocket", "Q Quadrature", "q")
        self.updateHideStatus()
        self.outputs.new("an_FloatSocket", "Alpha", "alpha")
        
    def draw(self, layout):
        layout.prop(self, "targetType", expand = True)
        
    def drawLabel(self):
        return "--> " + self.labelOperation + "a (linear)"
    
    def getExecutionCode(self):
        yield "r, g, b, h, s, v, l, y, i, q = 0, 0, 0, 0, 0, 0, 0, 0, 0, 0"
        if self.targetType == "RGB":    yield "r, g, b = color[0], color[1], color[2]"
        elif self.targetType == "HSV":  yield "h, s, v = colorsys.rgb_to_hsv(color[0], color[1], color[2])"
        elif self.targetType == "HSL":  yield "h, l, s = colorsys.rgb_to_hls(color[0], color[1], color[2])"#attention to the HLS order!
        elif self.targetType == "YIQ":  yield "y, i, q = colorsys.rgb_to_yiq(color[0], color[1], color[2])"
        yield "alpha = color[3]"
    
    def getUsedModules(self):
        return ["colorsys"]

    def updateHideStatus(self):
        self.outputs["Red"].hide = True
        self.outputs["Green"].hide = True
        self.outputs["Blue"].hide = True
        
        self.outputs["Hue"].hide = True
        self.outputs["Saturation"].hide = True
        self.outputs["Value"].hide = True
        
        self.outputs["Lightness"].hide = True
        
        self.outputs["Y Luma"].hide = True
        self.outputs["I In phase"].hide = True
        self.outputs["Q Quadrature"].hide = True
        
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