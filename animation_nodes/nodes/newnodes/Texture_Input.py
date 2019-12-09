import bpy
from bpy.props import *
from ... events import propertyChanged
from ... base_types import AnimationNode, VectorizedSocket
from ... data_structures import DoubleList, Color, ColorList

class TextureInputNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_TextureInputNode"
    bl_label = "Texture Input"

    useVectorList: VectorizedSocket.newProperty()
    autoRefreshBool: BoolProperty(name = "Auto Refresh", default = False, update = propertyChanged)    
    
    def create(self):
        self.newInput("Texture", "Texture", "texture", defaultDrawType = "PROPERTY_ONLY")
        self.newInput(VectorizedSocket("Vector", "useVectorList",
            ("Location", "location"), ("Locations", "locations")))
        self.newOutput(VectorizedSocket("Color", "useVectorList",
            ("Color", "color"), ("Colors", "colors")))
        self.newOutput(VectorizedSocket("Float", "useVectorList",
            ("Red", "red"), ("Reds", "reds")))
        self.newOutput(VectorizedSocket("Float", "useVectorList",
            ("Green", "green"), ("Greens", "greens")))
        self.newOutput(VectorizedSocket("Float", "useVectorList",
            ("Blue", "blue"), ("Blues", "blues")))
        self.newOutput(VectorizedSocket("Float", "useVectorList",
            ("Alpha / Luminance", "alpha"), ("Alphas / Luminances", "alphas")))
        self.newOutput("Generic", "Extra Settings", "texture")

        visibleOutputs = ("Color", "Colors")
        for socket in self.outputs:
            socket.hide = socket.name not in visibleOutputs

    def drawAdvanced(self, layout):
        layout.prop(self, "autoRefreshBool")
        box = layout.box()
        col = box.column(align = True)
        col.label(text = "Info", icon = "INFO")
        col.label(text = "For External Texture, Alpha Output = Alpha")
        col.label(text = "For Internal Texture, Alpha Output = Luminance")

    def getExecutionFunctionName(self):
        if self.useVectorList:
            return "executeList"
        else:
            return "executeSingle"

    def executeSingle(self, texture, location):
        if texture is None:
            return None, None, None, None, None, None
        
        if texture.image.source in ['SEQUENCE', 'MOVIE']: 
            texture.image_user.use_auto_refresh = self.autoRefreshBool

        color = Color(texture.evaluate(location))
        return color, color.r, color.g, color.b, color.a, texture
        
    def executeList(self, texture, locations):
        if texture is None or len(locations) == 0:
            return ColorList(), DoubleList(), DoubleList(), DoubleList(), DoubleList(), texture
        
        if texture.image.source in ['SEQUENCE', 'MOVIE']: 
            texture.image_user.use_auto_refresh = self.autoRefreshBool

        locationCount = len(locations)
        reds = DoubleList(length = locationCount)
        greens = DoubleList(length = locationCount)
        blues = DoubleList(length = locationCount)
        alphas = DoubleList(length = locationCount)
        colors = ColorList(length = locationCount)
        for i, location in enumerate(locations):
            color = Color(texture.evaluate(location))
            reds[i] = color.r
            greens[i] = color.g
            blues[i] = color.b
            alphas[i] = color.a 
            colors[i] = color
        return colors, reds, greens, blues, alphas, texture

