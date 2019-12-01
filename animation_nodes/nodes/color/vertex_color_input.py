import bpy
from bpy.props import *
from ... events import propertyChanged
from ... base_types import AnimationNode, VectorizedSocket
from ... data_structures import Color, ColorList, VirtualColorList, LongList
from . c_utils import getVertexColorsFromLoopColors, getPolygonColorsFromLoopColors

modeItems = [
    ("ALL", "All", "Get color of every vertex", "NONE", 0),
    ("INDEX", "Index", "Get color of a specific vertex", "NONE", 1)
]

colorModeItems = [
    ("LOOP", "Loop", "Set color of every loop vertex", "NONE", 0),
    ("VERTEX", "Vertex", "Set color of every vertex", "NONE", 1),
    ("POLYGON", "Polygon", "Set color of every polgon", "NONE", 2)    
]

colorLayerIdentifierTypeItems = [
    ("INDEX", "Index", "Get color layer based on the index", "NONE", 0),
    ("NAME", "Name", "Get color layer based on the name", "NONE", 1)
]

class VertexColorInputNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_VertexColorInputNode"
    bl_label = "Vertex Color Input"
    errorHandlingType = "EXCEPTION"

    mode: EnumProperty(name = "Mode", default = "ALL",
        items = modeItems, update = AnimationNode.refresh)

    colorMode: EnumProperty(name = "Color Mode", default = "LOOP",
        items = colorModeItems, update = AnimationNode.refresh)

    colorLayerIdentifierType: EnumProperty(name = "Color Layer Identifier Type", default = "INDEX",
        items = colorLayerIdentifierTypeItems, update = AnimationNode.refresh)

    useIndexList: VectorizedSocket.newProperty()

    def create(self):
        self.newInput("Object", "Object", "object", defaultDrawType = "PROPERTY_ONLY")

        if self.colorLayerIdentifierType == "INDEX":
            self.newInput("Integer", "Color Index", "colorLayerIndex")
        elif self.colorLayerIdentifierType == "NAME":
            self.newInput("Text", "Name", "colorLayerName")

        if self.mode == "INDEX":
            self.newInput(VectorizedSocket("Integer", "useIndexList",
                ("Index", "index"), ("Indices", "indices")))
            self.newOutput(VectorizedSocket("Color", "useIndexList",
                ("Color", "color"), ("Colors", "colors")))
        elif self.mode == "ALL":
            self.newOutput("Color List", "Colors", "colors")        

    def draw(self, layout):
        layout.prop(self, "mode", text = "")
        layout.prop(self, "colorMode", text = "")

    def drawAdvanced(self, layout):
        layout.prop(self, "colorLayerIdentifierType", text = "Type")

    def getExecutionFunctionName(self):
        if self.mode == "INDEX":
            if self.useIndexList:
                return "execute_Indices"
            else:
                return "execute_Index"
        elif self.mode == "ALL":
            return "execute_All"

    def execute_Index(self, object, identifier, index):
        if object is None:
            return None

        defaultColor = Color((0, 0, 0, 1))
        colorsList = VirtualColorList.create(self.getVertexColors(object, identifier), defaultColor)
        return colorsList[index]

    def execute_Indices(self, object, identifier, indices):
        if object is None:
            return ColorList()

        defaultColor = Color((0, 0, 0, 1))
        colorsList = VirtualColorList.create(self.getVertexColors(object, identifier), defaultColor)
        colors = ColorList(length = len(indices))
        
        for i, index in enumerate(indices):
            colors[i] = colorsList[index]
        return colors

    def execute_All(self, object, identifier):
        if object is None:
            return ColorList()
        
        return self.getVertexColors(object, identifier)

    def getVertexColors(self, object, identifier):
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
        
