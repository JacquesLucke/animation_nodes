import bpy
from bpy.props import *
from ... events import propertyChanged
from ... base_types import AnimationNode
from ... data_structures import Color, ColorList, VirtualColorList
from .. color.c_utils import getVertexColorsFromLoopColors, getPolygonColorsFromLoopColors

colorModeItems = [
    ("LOOP", "Loop", "Get color of every loop vertex", "NONE", 0),
    ("VERTEX", "Vertex", "Get color of every vertex", "NONE", 1),
    ("POLYGON", "Polygon", "Get color of every polygon", "NONE", 2)    
]

class GetVertexColorLayerNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_GetVertexColorLayerNode"
    bl_label = "Get Vertex Color Layer"
    errorHandlingType = "EXCEPTION"

    colorMode: EnumProperty(name = "Color Mode", default = "LOOP",
        items = colorModeItems, update = propertyChanged)

    def create(self):
        self.newInput("Mesh", "Mesh", "mesh")
        self.newInput("Text", "Name", "colorLayerName")

        self.newOutput("Color List", "Colors", "colors")        

    def draw(self, layout):
        layout.prop(self, "colorMode", text = "")

    def execute(self, mesh, colorLayerName):
        if colorLayerName == "":
            self.raiseErrorMessage("Vertex color layer name can't be empty.")
        
        defaultColor = Color((0, 0, 0, 1))
        
        colorsList = mesh.getVertexColors(colorLayerName)
        if colorsList is None:
            self.raiseErrorMessage(f"Mesh doesn't have a vertex color layer with the name '{colorLayerName}'.")

        if self.colorMode == "LOOP":
            return colorsList
        elif self.colorMode == "VERTEX":
            polygonIndices = mesh.polygons
            vertexCount = len(mesh.vertices)
            
            colorsList = VirtualColorList.create(colorsList, defaultColor)
            return getVertexColorsFromLoopColors(vertexCount, polygonIndices, colorsList)
        elif self.colorMode == "POLYGON":
            polygonIndices = mesh.polygons

            colorsList = VirtualColorList.create(colorsList, defaultColor)
            return getPolygonColorsFromLoopColors(polygonIndices, colorsList)
