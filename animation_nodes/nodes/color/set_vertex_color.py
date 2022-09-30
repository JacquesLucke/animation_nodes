import bpy
from bpy.props import *
from ... events import propertyChanged
from ... base_types import AnimationNode, VectorizedSocket
from ... data_structures import Color, ColorList, VirtualColorList
from . c_utils import getLoopColorsFromVertexColors, getLoopColorsFromPolygonColors

colorModeItems = [
    ("LOOP", "Loop", "Set color of every loop vertex", "NONE", 0),
    ("VERTEX", "Vertex", "Set color of every vertex", "NONE", 1),
    ("POLYGON", "Polygon", "Set color of every polygon", "NONE", 2)    
]

colorLayerIdentifierTypeItems = [
    ("INDEX", "Index", "Get vertex color layer based on the index", "NONE", 0),
    ("NAME", "Name", "Get vertex color layer based on the name", "NONE", 1)
]

class SetVertexColorNode(AnimationNode, bpy.types.Node):
    bl_idname = "an_SetVertexColorNode"
    bl_label = "Set Vertex Color"
    errorHandlingType = "EXCEPTION"

    colorMode: EnumProperty(name = "Color Mode", default = "LOOP",
        items = colorModeItems, update = propertyChanged)

    colorLayerIdentifierType: EnumProperty(name = "Color Layer Identifier Type", default = "INDEX",
        items = colorLayerIdentifierTypeItems, update = AnimationNode.refresh)

    useColorList: VectorizedSocket.newProperty()

    def create(self):
        self.newInput("Object", "Object", "object", defaultDrawType = "PROPERTY_ONLY")

        if self.colorLayerIdentifierType == "INDEX":
            self.newInput("Integer", "Vertex Color Index", "vertexColorIndex")
        elif self.colorLayerIdentifierType == "NAME":
            self.newInput("Text", "Name", "colorLayerName")

        self.newInput(VectorizedSocket("Color", "useColorList",
            ("Color", "color"), ("Colors", "colors")))

        self.newOutput("Object", "Object", "outObject")

    def draw(self, layout):
        if self.useColorList:
            layout.prop(self, "colorMode", text = "")

    def drawAdvanced(self, layout):
        layout.prop(self, "colorLayerIdentifierType", text = "Type")

    def getExecutionFunctionName(self):
        if self.useColorList:
            return "execute_ColorsList"
        else:
            return "execute_SingleColor"

    def execute_SingleColor(self, object, identifier, color):
        if object is None: return
        
        defaultColor = Color((0, 0, 0, 1))
        colorLayer = self.getVertexColorLayer(object, identifier)

        colorsList = VirtualColorList.create(color, defaultColor).materialize(len(colorLayer.data))

        colorLayer.data.foreach_set("color", colorsList.asNumpyArray())
        object.data.update()
        return object  
        
    def execute_ColorsList(self, object, identifier, colors):
        if object is None: return
        
        defaultColor = Color((0, 0, 0, 1))
        colorsList = VirtualColorList.create(colors, defaultColor)
        colorLayer = self.getVertexColorLayer(object, identifier)
        
        if self.colorMode == "LOOP":
            colorsList = colorsList.materialize(len(colorLayer.data))
        elif self.colorMode == "VERTEX":
            sourceMesh = object.an.getMesh(False)
            polygonIndices = sourceMesh.an.getPolygonIndices()
            colorsList = getLoopColorsFromVertexColors(polygonIndices, colorsList) 
        elif self.colorMode == "POLYGON":
            sourceMesh = object.an.getMesh(False)
            polygonIndices = sourceMesh.an.getPolygonIndices()
            colorsList = getLoopColorsFromPolygonColors(polygonIndices, colorsList)
        
        colorLayer.data.foreach_set("color", colorsList.asNumpyArray())
        object.data.update()
        return object 

    def getVertexColorLayer(self, object, identifier):
        if object.type != "MESH": 
            self.raiseErrorMessage("No mesh object.")
        
        if object.mode == "EDIT":
            self.raiseErrorMessage("Object is not in object mode.")

        try: return object.data.vertex_colors[identifier]
        except: self.raiseErrorMessage("Color Layer is not found.")

