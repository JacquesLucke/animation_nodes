from itertools import chain
import bpy
import numpy
from bpy.props import *
from mathutils import Color
from ... events import propertyChanged
from ... base_types import AnimationNode, VectorizedSocket

class SetVertexColorsNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_SetVertexColorsNode"
    bl_label = "Set Vertex Colors"
    errorHandlingType = "EXCEPTION"

    vertexColorName: StringProperty(name = "Vertex Color Group", default = "Col", update = propertyChanged)
    checkIfColorIsSet: BoolProperty(default = True)
    useColorList: VectorizedSocket.newProperty()
    messageInfo: StringProperty()

    def create(self):
        self.newInput("Object", "Object", "object").defaultDrawType = "PROPERTY_ONLY"
        self.newInput(VectorizedSocket("Color", "useColorList",
            ("Color", "color"), ("Colors", "colors")))
        self.newOutput("Object", "Object", "outObject")

    def draw(self, layout):
        layout.prop(self, "vertexColorName", text = "", icon = "GROUP_VCOL")
        if (self.messageInfo != ""):
            layout.label(text = self.messageInfo, icon="INFO")

    def drawAdvanced(self, layout):
        layout.prop(self, "checkIfColorIsSet", text = "Check Color")
        
    def getExecutionFunctionName(self):
        if self.useColorList:
            return "executeColors"
        else:
            return "executeColor"

    def executeColor(self, object, color):
        if object is None: return object
        if object.type != "MESH": return object
        if object.mode == "EDIT":
            self.raiseErrorMessage("Object is in edit mode")
            return object
        colorLayer = getVertexColorLayer(object, self.vertexColorName)
        if len(colorLayer.data) == 0: return object
        newColorAsArray = numpy.array(colorList(self, color), dtype = "f")
        colors = numpy.tile(newColorAsArray, len(colorLayer.data))
        colorLayer.data.foreach_set("color", colors)
        object.data.update()
        return object  
        
    def executeColors(self, object, colors):
        if object is None: return object
        if object.type != "MESH": return object
        if object.mode == "EDIT":
            self.raiseErrorMessage("Object is in edit mode")
            return object
        colorLayer = getVertexColorLayer(object, self.vertexColorName)
        if len(colorLayer.data) == 0: return object
        self.messageInfo = "Vertices: " + str(len(colorLayer.data))
        colorLayer.data.foreach_set("color", colorsList(self, colors))
        object.data.update()       
        return object       

def colorsList(self, colors):
    return list(chain.from_iterable(colors))

def colorList(self, color):
    flist = []
    for val in color:
        flist.append(val)     
    return flist
        
def getVertexColorLayer(object, name):
    try: return object.data.vertex_colors[name]
    except: return object.data.vertex_colors.new(name = name)
