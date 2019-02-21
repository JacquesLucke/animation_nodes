import bpy
from bpy.props import *
from ... events import propertyChanged
from ... data_structures import DoubleList
from ... base_types import AnimationNode, VectorizedSocket

modeItems = [
    ("ALL", "All", "Get weight of every vertex", "NONE", 0),
    ("INDEX", "Index", "Get weight of a specific vertex", "NONE", 1)
]

groupIdentifierTypeItems = [
    ("INDEX", "Index", "Get vertex group based on the index", "NONE", 0),
    ("NAME", "Name", "Get vertex group based on the name", "NONE", 1)
]

layerNotFoundMessage = "color layer not found"
noMeshMessage = "no mesh object"

class VertexColorInputNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_VertexColorInputNode"
    bl_label = "Vertex Color Input"
    errorHandlingType = "EXCEPTION"

    mode: EnumProperty(name = "Mode", default = "ALL",
        items = modeItems, update = AnimationNode.refresh)

    groupIdentifierType: EnumProperty(name = "Group Identifier Type", default = "INDEX",
        items = groupIdentifierTypeItems, update = AnimationNode.refresh)

    useIndexList: VectorizedSocket.newProperty()

    def create(self):
        self.newInput("Object", "Object", "object", defaultDrawType = "PROPERTY_ONLY")

        if self.groupIdentifierType == "INDEX":
            self.newInput("Integer", "Color Index", "groupIndex")
        elif self.groupIdentifierType == "NAME":
            self.newInput("Text", "Name", "groupName")

        if self.mode == "INDEX":
            self.newInput(VectorizedSocket("Integer", "useIndexList",
                ("Weight Index", "index"), ("Weight Indices", "indices")))
            self.newOutput(VectorizedSocket("Color", "useIndexList",
                ("Vertex Color", "color"), ("Vertex Colors", "colors")))
            self.newOutput("Float List", "Vertex Flat Colors", "vertfatcolors")        
        elif self.mode == "ALL":
            self.newOutput("Color List", "Vertex Colors", "colors")        
            self.newOutput("Float List", "Vertex Flat Colors", "vertfatcolors")        

    def draw(self, layout):
        layout.prop(self, "mode", text = "")

    def drawAdvanced(self, layout):
        layout.prop(self, "groupIdentifierType", text = "Type")

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
            return 0, []

        colorLayer = self.getVertexColorLayer(object, identifier)
        if colorLayer is None:
            self.raiseErrorMessage(layerNotFoundMessage)
            
        colorLayer = self.getVertexColorLayer(object, identifier)
        getColor, vertfatcolors = self.getColorList(colorLayer) 
        try: return getColor[index], vertfatcolors
        except: return None, vertfatcolors

    def execute_Indices(self, object, identifier, indices):
        if object is None:
            return [], []
        colorLayer = self.getVertexColorLayer(object, identifier)
        if colorLayer is None:
            if object is not None:
                self.raiseErrorMessage(layerNotFoundMessage)
            return DoubleList()

        colorLayer = self.getVertexColorLayer(object, identifier)
        getColor, vertfatcolors = self.getColorList(colorLayer)
        colors = []
        for i, index in enumerate(indices):
            try: colors.append(getColor[index])
            except: colors.append([0., 0., 0., 0.])
        return colors, vertfatcolors

    def execute_All(self, object, identifier):
        if object is None:
            return [], []

        if object.type != "MESH":
            self.raiseErrorMessage(noMeshMessage)

        colorLayer = self.getVertexColorLayer(object, identifier)
        if colorLayer is None:
            self.raiseErrorMessage(layerNotFoundMessage)

        colorLayer = self.getVertexColorLayer(object, identifier)
        return self.getColorList(colorLayer)

    def getColorList(self, colorLayer):
        colorFlatList = self.getVertexColors(colorLayer)
        colorlist = []
        for i in range(int(len(colorFlatList)/4)):
            colorlist.append(colorFlatList[i*4: (i+1)*4])
        return colorlist, colorFlatList
            
    def getVertexColors(self, colorLayer):
        colorFlatList = [0.]*len(colorLayer.data)*4
        colorLayer.data.foreach_get("color", colorFlatList)
        return colorFlatList

    def getVertexColorLayer(self, object, identifier):
        try: return object.data.vertex_colors[identifier]
        except: return None
