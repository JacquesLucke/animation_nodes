import bpy
from bpy.props import *
from ... events import propertyChanged
from ... data_structures import DoubleList
from ... base_types import AnimationNode, VectorizedSocket

class TextureInputNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_TextureInputNode"
    bl_label = "Texture Input"

    useVectorList: VectorizedSocket.newProperty()
    autoRefreshBool: BoolProperty(name="Auto Refresh", default=False, update=propertyChanged)    
    
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
        col.label(text = "Info", icon="INFO")
        col.label(text = "For External Texture, Alpha Output = Alpha")
        col.label(text = "For Internal Texture, Alpha Output = Luminance")

    def getExecutionFunctionName(self):
        if self.useVectorList:
            return "executeList"
        else:
            return "executeSingle"

    def executeSingle(self, texture, location):
        if len(bpy.data.textures) < 1 or texture is None:
            return None, None, None, None, None, None
        try:    
            texture.image_user.use_auto_refresh = self.autoRefreshBool
        except:
            pass

        color = texture.evaluate(location)[:]
        red = color[0]
        green = color[1]
        blue = color[2]
        alpha = color[3]     
        return color, red, green, blue, alpha, texture
        
    def executeList(self, texture, locations):
        reds = []
        greens = []
        blues = []
        alphas = []
        colors = []
        if len(bpy.data.textures) < 1 or texture is None:
            return colors, DoubleList.fromValues(reds), DoubleList.fromValues(greens), DoubleList.fromValues(blues), DoubleList.fromValues(alphas), None
        if locations is None or len(locations) < 1:
            return colors, DoubleList.fromValues(reds), DoubleList.fromValues(greens), DoubleList.fromValues(blues), DoubleList.fromValues(alphas), texture
        try:    
            texture.image_user.use_auto_refresh = self.autoRefreshBool
        except:
            pass

        for location in locations:
            color = texture.evaluate(location)[:]
            reds.append(color[0])
            greens.append(color[1])
            blues.append(color[2])
            alphas.append(color[3])
            colors.append(color)     
        return colors, DoubleList.fromValues(reds), DoubleList.fromValues(greens), DoubleList.fromValues(blues), DoubleList.fromValues(alphas), texture