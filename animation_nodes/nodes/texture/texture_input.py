import bpy
from . c_utils import getTextureColors
from ... base_types import AnimationNode, VectorizedSocket
from ... data_structures import DoubleList, Color, ColorList

class TextureInputNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_TextureInputNode"
    bl_label = "Texture Input"

    useVectorList: VectorizedSocket.newProperty()

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

        visibleOutputs = ("Color", "Colors")
        for socket in self.outputs:
            socket.hide = socket.name not in visibleOutputs

    def drawAdvanced(self, layout):
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

        color = Color(texture.evaluate(location))
        return color, color.r, color.g, color.b, color.a

    def executeList(self, texture, locations):
        if texture is None or len(locations) == 0:
            return ColorList(), DoubleList(), DoubleList(), DoubleList(), DoubleList()

        return getTextureColors(texture, locations)
