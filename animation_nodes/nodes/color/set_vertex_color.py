import bpy
import numpy
from bpy.props import *
from itertools import chain
from ... events import propertyChanged
from ... base_types import AnimationNode, VectorizedSocket

modeItems = [
    ("LOOPS", "Loops", "Set color of every loop vertex", "NONE", 0),
    ("VERTICES", "Vertices", "Set color of every vertex", "NONE", 1),
    ("POLYGONS", "Polygons", "Set color of every polgon", "NONE", 2)    
]

colorLayerIdentifierTypeItems = [
    ("INDEX", "Index", "Get vertex color layer based on the index", "NONE", 0),
    ("NAME", "Name", "Get vertex color layer based on the name", "NONE", 1)
]

class SetVertexColorNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_SetVertexColorNode"
    bl_label = "Set Vertex Color"
    errorHandlingType = "EXCEPTION"

    mode: EnumProperty(name = "Mode", default = "LOOPS",
        items = modeItems, update = AnimationNode.refresh)

    colorLayerIdentifierType: EnumProperty(name = "Color Layer Identifier Type", default = "INDEX",
        items = colorLayerIdentifierTypeItems, update = AnimationNode.refresh)

    useColorList: VectorizedSocket.newProperty()

    def create(self):
        self.newInput("Object", "Object", "object", defaultDrawType = "PROPERTY_ONLY")

        if self.colorLayerIdentifierType == "INDEX":
            self.newInput("Integer", "Color Index", "colorLayerIndex")
        elif self.colorLayerIdentifierType == "NAME":
            self.newInput("Text", "Name", "colorLayerName")

        self.newInput(VectorizedSocket("Color", "useColorList",
            ("Color", "color"), ("Colors", "colors")))

        self.newOutput("Object", "Object", "outObject")

    def draw(self, layout):
        layout.prop(self, "mode", text = "")

    def drawAdvanced(self, layout):
        layout.prop(self, "colorLayerIdentifierType", text = "Type")

    def getExecutionFunctionName(self):
        if self.useColorList:
            return "execute_ColorsList"
        else:
            return "execute_SingleColor"

    def execute_SingleColor(self, object, identifier, color):
        if object is None: return
        colorLayer = self.getVertexColorLayer(object, identifier)

        colorsList = numpy.tile(numpy.array(color, dtype = "f"), len(colorLayer.data))
        
        colorLayer.data.foreach_set("color", colorsList)
        object.data.update()
        return object  
        
    def execute_ColorsList(self, object, identifier, colors):
        if object is None: return

        if self.mode == "LOOPS":
            return self.setVertexColorForLoops(object, identifier, colors) 

        elif self.mode == "VERTICES":
            return self.setVertexColorForVertices(object, identifier, colors)

        elif self.mode == "POLYGONS":
            return self.setVertexColorForPolygons(object, identifier, colors)

    def setVertexColorForLoops(self, object, identifier, colors):
        colorLayer = self.getVertexColorLayer(object, identifier)
        
        loops = object.data.loops
        if len(colors) < len(loops): return object

        loopsColors = []
        for loop in loops:
            loopsColors.extend(colors[loop.vertex_index])
      
        colorLayer.data.foreach_set("color", loopsColors)
        object.data.update()
        return object

    def setVertexColorForVertices(self, object, identifier, colors):
        colorLayer = self.getVertexColorLayer(object, identifier)
        
        if len(colors) < len(colorLayer.data): return object

        colorLayer.data.foreach_set("color", colorsFlatList(self, colors))
        object.data.update()
        return object

    def setVertexColorForPolygons(self, object, identifier, colors):
        colorLayer = self.getVertexColorLayer(object, identifier)
        
        if len(colors) < len(object.data.polygons): return object

        polygonsColors = []
        for i, polygon in enumerate(object.data.polygons):
            polygonsColors.extend(list(colors[i])*len(polygon.loop_indices))
       
        colorLayer.data.foreach_set("color", polygonsColors)
        object.data.update()
        return object 

    def getVertexColorLayer(self, object, identifier):
        if object.type != "MESH": 
            self.raiseErrorMessage("No mesh object.")
        
        if object.mode == "EDIT":
            self.raiseErrorMessage("Object is not in object mode.")

        try: return object.data.vertex_colors[identifier]
        except: self.raiseErrorMessage("Color Layer is not found.")

<<<<<<< HEAD
def colorsFlatList(self, colors):
    return list(chain.from_iterable(colors))
=======
def colorsAreEqual(a, b):
    return abs((a[0] * 1000 + a[1] * 100 + a[2] * 10 + a[3])
              -(b[0] * 1000 + b[1] * 100 + b[2] * 10 + b[3])) < 0.001
>>>>>>> master
