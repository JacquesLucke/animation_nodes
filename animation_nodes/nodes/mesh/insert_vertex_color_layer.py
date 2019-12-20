import bpy
from bpy.props import *
from ... events import propertyChanged
from ... base_types import AnimationNode, VectorizedSocket
from ... data_structures import Color, ColorList, VirtualColorList
from .. color.c_utils import getLoopColorsFromVertexColors, getLoopColorsFromPolygonColors

colorModeItems = [
    ("LOOP", "Loop", "Get color of every loop vertex", "NONE", 0),
    ("VERTEX", "Vertex", "Get color of every vertex", "NONE", 1),
    ("POLYGON", "Polygon", "Get color of every polygon", "NONE", 2)    
]
       
class InsertVertexColorLayerNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_InsertVertexColorLayerNode"
    bl_label = "Insert Vertex Color Layer"
    bl_width_default = 155
    errorHandlingType = "EXCEPTION"

    colorMode: EnumProperty(name = "Color Mode", default = "LOOP",
        items = colorModeItems, update = propertyChanged)

    useColorList: VectorizedSocket.newProperty()

    def create(self):
        self.newInput("Mesh", "Mesh", "mesh", dataIsModified = True)
        self.newInput("Text", "Name", "colorLayerName", value = "AN-Col")
        self.newInput(VectorizedSocket("Color", "useColorList",
            ("Color", "color"), ("Colors", "colors")))
        self.newOutput("Mesh", "Mesh", "mesh")

    def draw(self, layout):
        if self.useColorList:
            layout.prop(self, "colorMode", text = "")

    def getExecutionFunctionName(self):
        if self.useColorList:
            return "execute_ColorsList"
        else:
            return "execute_SingleColor"

    def execute_SingleColor(self, mesh, colorLayerName, color):
        if mesh is None: return None
        if colorLayerName == "": 
            self.raiseErrorMessage("No Vertex Color Layer Name.")
        elif colorLayerName in mesh.getVertexColorLayerNames():
            self.raiseErrorMessage(f"Mesh has already this Vertex Color Layer."
                                   f" Layers: {', '.join(mesh.getVertexColorLayerNames())}")

        defaultColor = Color((0, 0, 0, 1))
        colorsList = VirtualColorList.create(color, defaultColor).materialize(len(mesh.polygons.indices))
        
        mesh.insertVertexColorLayer(colorLayerName, colorsList)
        return mesh
        
    def execute_ColorsList(self, mesh, colorLayerName, colors):
        if mesh is None: return None
        if colorLayerName == "":
            self.raiseErrorMessage("No Vertex Color Layer Name.")
        elif colorLayerName in mesh.getVertexColorLayerNames():
            self.raiseErrorMessage(f"Mesh has already this Vertex Color Layer."
                                   f" Layers: {', '.join(mesh.getVertexColorLayerNames())}")

        defaultColor = Color((0, 0, 0, 1))
        colorsList = VirtualColorList.create(colors, defaultColor)
        
        if self.colorMode == "LOOP":
            colorsList = colorsList.materialize(len(mesh.polygons.indices))
        elif self.colorMode == "VERTEX":
            polygonIndices = mesh.polygons
            colorsList = getLoopColorsFromVertexColors(polygonIndices, colorsList) 
        elif self.colorMode == "POLYGON":
            polygonIndices = mesh.polygons
            colorsList = getLoopColorsFromPolygonColors(polygonIndices, colorsList)
        
        mesh.insertVertexColorLayer(colorLayerName, colorsList)
        return mesh
        
