import bpy
from bpy.props import *
from ... events import propertyChanged
from ... base_types import AnimationNode, VectorizedSocket
from ... data_structures import Color, ColorList, VirtualColorList
from . c_utils import getVertexColorsFromLoopColors, getPolygonColorsFromLoopColors

colorModeItems = [
    ("LOOP", "Loop", "Get color of every loop vertex", "NONE", 0),
    ("VERTEX", "Vertex", "Get color of every vertex", "NONE", 1),
    ("POLYGON", "Polygon", "Get color of every polgon", "NONE", 2)    
]

colorLayerIdentifierTypeItems = [
    ("INDEX", "Index", "Get color layer based on the index", "NONE", 0),
    ("NAME", "Name", "Get color layer based on the name", "NONE", 1)
]

class VertexColorInputNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_VertexColorInputNode"
    bl_label = "Vertex Color Input"
    errorHandlingType = "EXCEPTION"

    colorMode: EnumProperty(name = "Color Mode", default = "LOOP",
        items = colorModeItems, update = AnimationNode.refresh)

    colorLayerIdentifierType: EnumProperty(name = "Color Layer Identifier Type", default = "INDEX",
        items = colorLayerIdentifierTypeItems, update = AnimationNode.refresh)

    useIndexList: VectorizedSocket.newProperty()

    def create(self):
        self.newInput("Object", "Object", "object", defaultDrawType = "PROPERTY_ONLY")

        if self.colorLayerIdentifierType == "INDEX":
            self.newInput("Integer", "Vertex Color Index", "vertexColorIndex")
        elif self.colorLayerIdentifierType == "NAME":
            self.newInput("Text", "Name", "colorLayerName")

        self.newOutput("Color List", "Colors", "colors")        

    def draw(self, layout):
        layout.prop(self, "colorMode", text = "")

    def drawAdvanced(self, layout):
        layout.prop(self, "colorLayerIdentifierType", text = "Type")

    def execute(self, object, identifier):
        if object is None: return
        
        colorLayer = self.getVertexColorLayer(object, identifier)
        defaultColor = Color((0, 0, 0, 1))
        
        colorsList = ColorList(length = len(colorLayer.data))
        colorLayer.data.foreach_get("color", colorsList.asNumpyArray())

        if self.colorMode == "LOOP":
            return colorsList

        elif self.colorMode == "VERTEX":
            sourceMesh = object.an.getMesh(False)
            polygonIndices = sourceMesh.an.getPolygonIndices()
            vertexCount = len(sourceMesh.vertices)
            
            colorsList = VirtualColorList.create(colorsList, defaultColor)
            return getVertexColorsFromLoopColors(vertexCount, polygonIndices, colorsList)

        elif self.colorMode == "POLYGON":
            sourceMesh = object.an.getMesh(False)
            polygonIndices = sourceMesh.an.getPolygonIndices()

            colorsList = VirtualColorList.create(colorsList, defaultColor)
            return getPolygonColorsFromLoopColors(polygonIndices, colorsList)
        
    def getVertexColorLayer(self, object, identifier):
        if object.type != "MESH": 
            self.raiseErrorMessage("No mesh object.")
        
        if object.mode == "EDIT":
            self.raiseErrorMessage("Object is not in object mode.")

        try: return object.data.vertex_colors[identifier]
        except: self.raiseErrorMessage("Color Layer is not found.")
        
