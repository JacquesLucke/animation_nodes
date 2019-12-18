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

class GetMeshVertexColorNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_GetMeshVertexColorNode"
    bl_label = "Get Mesh Vertex Color"
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
        if mesh is None or colorLayerName not in mesh.getVertexColorLayerNames(): return ColorList()

        defaultColor = Color((0, 0, 0, 1))
        
        colorsList = ColorList(length = len(mesh.polygons.indices))
        
        for name, data in mesh.getVertexColorLayers():
            if name == colorLayerName:
                colorsList = data

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
        
    