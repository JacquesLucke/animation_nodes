import bpy
from bpy.props import *
from ... data_structures import Layer
from ... events import propertyChanged
from ... base_types import AnimationNode, VectorizedSocket

layerTypeItems = [
    ("ALL", "All", "Get all grease layers", "NONE", 0),
    ("INDEX", "Index", "Get a specific grease layer", "NONE", 1) 
]

layerIdentifierTypeItems = [
    ("INDEX", "Index", "Get grease layer based on the index", "NONE", 0),
    ("NAME", "Name", "Get grease layer based on the name", "NONE", 1)
]

class GPencilObjectInputNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_GPencilObjectInputNode"
    bl_label = "GPencil Object Input"
    bl_width_default = 165

    useGenericList: VectorizedSocket.newProperty()
    
    layerType: EnumProperty(name = "Layer Type", default = "INDEX",
        items = layerTypeItems, update = AnimationNode.refresh)

    layerIdentifierType: EnumProperty(name = "Layer Identifier Type", default = "INDEX",
        items = layerIdentifierTypeItems, update = AnimationNode.refresh)
    
    def create(self):
        self.newInput("Object", "Object", "object", defaultDrawType = "PROPERTY_ONLY")
        self.newInput("Boolean", "Use World Space", "useWorldSpace")
         
        if self.layerType == "INDEX":
            if self.layerIdentifierType == "INDEX":
                self.newInput("Integer", "Layer Index", "layerIndex")
            elif self.layerIdentifierType == "NAME":
                self.newInput("Text", "Name", "layerName")        
            self.newOutput("Layer", "GPencil Layer", "gpencilLayer")
        elif self.layerType == "ALL":
            self.newOutput("Layer List", "GPencil Layers", "gpencilLayers")

    def draw(self, layout):
        layout.prop(self, "layerType", text = "")

    def drawAdvanced(self, layout):
        layout.prop(self, "layerIdentifierType", text = "Type")

    def getExecutionFunctionName(self):
        if self.layerType == "INDEX":
            return "executeSingle"
        elif self.layerType == "ALL":
            return "executeList"
        
    def executeSingle(self, object, useWorldSpace, identifier):
        if object is None or object.type != "GPENCIL": return Layer()
        if useWorldSpace:
            worldMatrix = object.matrix_world
        else:
            worldMatrix = None
        return Layer(self.getLayer(object, identifier), worldMatrix)

    def executeList(self, object, useWorldSpace):
        if object is None or object.type != "GPENCIL": return []
        if useWorldSpace:
            worldMatrix = object.matrix_world
        else:
            worldMatrix = None
        gpencilLayers = []
        for gpLayer in self.getLayers(object):
            gpencilLayers.append(Layer(gpLayer, worldMatrix))
        return gpencilLayers

    def getLayer(self, object, identifier):
        try:
            if type(identifier) == int:
                layers = self.copyObjectData(object).layers
                lenLayer = len(layers)
                index = lenLayer - 1 - identifier
                if index < 0: return None
                return layers[index]
            else: return self.copyObjectData(object).layers[identifier]
        except: return None
        
    def getLayers(self, object):
        try: return self.copyObjectData(object).layers
        except: return None

    def copyObjectData(self, object):
        objectName = object.name
        copyObjectName = "an_gcopy_" + objectName
        if copyObjectName in bpy.data.grease_pencils:
            oldCopyObject =  bpy.data.grease_pencils[copyObjectName]
            bpy.data.grease_pencils.remove(oldCopyObject)
        copyData = object.data.copy()
        copyData.name = copyObjectName
        return copyData