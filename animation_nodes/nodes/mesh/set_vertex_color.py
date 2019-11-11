import bpy
import numpy
from bpy.props import *
from itertools import chain
from mathutils import Color
from ... events import propertyChanged
from ... data_structures import VirtualDoubleList
from ... base_types import AnimationNode, VectorizedSocket

modeItems = [
    ("ALL", "All", "Set color of every vertex", "NONE", 0),
    ("INDEX", "Index", "Set color of a specific vertex", "NONE", 1)
]

colorLayerIdentifierTypeItems = [
    ("INDEX", "Index", "Get vertex color layer based on the index", "NONE", 0),
    ("NAME", "Name", "Get vertex color layer based on the name", "NONE", 1)
]

class SetVertexColorsNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_SetVertexColorsNode"
    bl_label = "Set Vertex Colors"
    errorHandlingType = "EXCEPTION"

    mode: EnumProperty(name = "Mode", default = "ALL",
        items = modeItems, update = AnimationNode.refresh)

    colorLayerIdentifierType: EnumProperty(name = "Color Layer Identifier Type", default = "INDEX",
        items = colorLayerIdentifierTypeItems, update = AnimationNode.refresh)

    useIndexList: VectorizedSocket.newProperty()
    useColorList: VectorizedSocket.newProperty()

    def create(self):
        self.newInput("Object", "Object", "object", defaultDrawType = "PROPERTY_ONLY")

        if self.colorLayerIdentifierType == "INDEX":
            self.newInput("Integer", "Color Index", "colorLayerIndex")
        elif self.colorLayerIdentifierType == "NAME":
            self.newInput("Text", "Name", "colorLayerName")

        if self.mode == "INDEX":
            self.newInput(VectorizedSocket("Integer", "useIndexList",
                ("Index", "index"), ("Indices", "indices")))
                
        self.newInput(VectorizedSocket("Color", ["useColorList", "useIndexList"],
            ("Color", "color"), ("Colors", "colors")))

        self.newOutput("Object", "Object", "outObject")

    def draw(self, layout):
        layout.prop(self, "mode", text = "")

    def drawAdvanced(self, layout):
        layout.prop(self, "colorLayerIdentifierType", text = "Type")

    def getExecutionFunctionName(self):
        if self.mode == "INDEX":
            if self.useIndexList:
                if self.useColorList:
                    return "execute_Indices_ColorsList"
                else:
                    return "execute_Indices_SingleColor"
            else:
                return "execute_Index_Color"

        elif self.mode == "ALL":
            if self.useColorList:
                return "execute_All_ColorsList"
            else:
                return "execute_All_SingleColor"

    def execute_Index_Color(self, object, identifier, index, color):
        if object is None: return
        colorLayer = self.getVertexColorLayer(object, identifier)
    
        newColor = [0, 0, 0, 1]   
        colorsList = numpy.tile(numpy.array(newColor, dtype = "f"), len(colorLayer.data))
        for i, value in enumerate(color):
            colorsList[i + index * 4] = value

        colorLayer.data.foreach_set("color", colorsList)
        object.data.update() 
        return object  

    def execute_Indices_SingleColor(self, object, identifier, indices, color):
        if object is None: return
        colorLayer = self.getVertexColorLayer(object, identifier)

        newColor = [0, 0, 0, 1]   
        colorsList = numpy.tile(numpy.array(newColor, dtype = "f"), len(colorLayer.data))
        for index in indices:
            for i, value in enumerate(color):
                colorsList[i + index * 4] = value

        colorLayer.data.foreach_set("color", colorsList)
        object.data.update()
        return object

    def execute_Indices_ColorsList(self, object, identifier, indices, colors):
        if object is None: return
        colorLayer = self.getVertexColorLayer(object, identifier)

        newColor = [0, 0, 0, 1]   
        colorsList = numpy.tile(numpy.array(newColor, dtype = "f"), len(colorLayer.data))
        for i, index in enumerate(indices):
            color = colors[i]
            for j, value in enumerate(color):
                colorsList[j + index * 4] = value
                
        colorLayer.data.foreach_set("color", colorsList)
        object.data.update()
        return object

    def execute_All_SingleColor(self, object, identifier, color):
        if object is None: return
        colorLayer = self.getVertexColorLayer(object, identifier)

        colorsList = numpy.tile(numpy.array(colorFlatList(self, color), dtype = "f"), len(colorLayer.data))
        
        colorLayer.data.foreach_set("color", colorsList)
        object.data.update()
        return object  
        
    def execute_All_ColorsList(self, object, identifier, colors):
        if object is None: return
        colorLayer = self.getVertexColorLayer(object, identifier)

        colorLayer.data.foreach_set("color", colorsFlatList(self, colors))
        object.data.update()       
        return object

    def getVertexColorLayer(self, object, identifier):
        if object.type != "MESH": 
            self.raiseErrorMessage("No mesh object.")
        
        if object.mode == "EDIT":
            self.raiseErrorMessage("Object is not in object mode.")

        try: return object.data.vertex_colors[identifier]
        except: self.raiseErrorMessage("Color Layer is not found.")

def colorsFlatList(self, colors):
    return list(chain.from_iterable(colors))

def colorFlatList(self, color):
    floatlist = []
    for value in color:
        floatlist.append(value)     
    return floatlist
        