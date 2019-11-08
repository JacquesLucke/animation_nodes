import bpy
from bpy.props import *
from ... events import propertyChanged
from ... base_types import AnimationNode, VectorizedSocket

modeItems = [
    ("ALL", "All", "Set weight of every vertex", "NONE", 0),
    ("INDEX", "Index", "Set weight of a specific vertex", "NONE", 1)
]

groupIdentifierTypeItems = [
    ("INDEX", "Index", "Get vertex group based on the index", "NONE", 0),
    ("NAME", "Name", "Get vertex group based on the name", "NONE", 1)
]

noMeshMessage = "no mesh object"
editMeshMessage = "object is not in object mode"

class VertexWeights(bpy.types.Node, AnimationNode):
    bl_idname = "an_SetVertexWeights"
    bl_label = "Set Vertex Weights"
    errorHandlingType = "EXCEPTION"

    mode: EnumProperty(name = "Mode", default = "ALL",
        items = modeItems, update = AnimationNode.refresh)

    groupIdentifierType: EnumProperty(name = "Group Identifier Type", default = "INDEX",
        items = groupIdentifierTypeItems, update = AnimationNode.refresh)

    useIndexList: VectorizedSocket.newProperty()
    useFloatList: VectorizedSocket.newProperty()
 
    def create(self):
        self.newInput("Object", "Object", "object", defaultDrawType = "PROPERTY_ONLY")

        if self.groupIdentifierType == "INDEX":
            self.newInput("Integer", "Group Index", "groupIndex")
        elif self.groupIdentifierType == "NAME":
            self.newInput("Text", "Name", "groupName")

        if self.mode == "INDEX":
            self.newInput(VectorizedSocket("Integer", "useIndexList",
                ("Index", "index"), ("Indices", "indices")))
            self.newInput(VectorizedSocket("Float", "useFloatList",
                ("Weight", "weight"), ("Weights", "weights")))
        elif self.mode == "ALL":
            self.newInput(VectorizedSocket("Float", "useFloatList",
                ("Weight", "weight"), ("Weights", "weights")))
        
        self.newOutput("Object", "Object", "object")

    def draw(self, layout):
        layout.prop(self, "mode", text = "")

    def drawAdvanced(self, layout):
        layout.prop(self, "groupIdentifierType", text = "Type")

    def getExecutionFunctionName(self):
        if self.mode == "INDEX":
            if self.useIndexList:
                if self.useFloatList:
                    return "execute_IndicesList"
                else:
                    return "execute_IndicesSingle"
            else:
                return "execute_Index"
        elif self.mode == "ALL":
            if self.useFloatList:
                return "execute_AllList"
            else:
                return "execute_AllSingle"

    def execute_Index(self, object, identifier, index, weight):
        if object is None: return
        if object.type != "MESH": 
            self.raiseErrorMessage(noMeshMessage)
        if object.mode == "EDIT":
            self.raiseErrorMessage(editMeshMessage)

        vertexGroup = self.getVertexGroup(object, identifier)

        vertexGroup.add([index], weight, "REPLACE")
        object.data.update()    
        return object

    def execute_IndicesSingle(self, object, identifier, indices, weight):
        if object is None: return
        if object.type != "MESH": 
            self.raiseErrorMessage(noMeshMessage)
        if object.mode == "EDIT":
            self.raiseErrorMessage(editMeshMessage)

        vertexGroup = self.getVertexGroup(object, identifier)

        vertexGroup.add(indices, weight, "REPLACE")
        object.data.update()    
        return object

    def execute_IndicesList(self, object, identifier, indices, weights):
        if object is None: return
        if object.type != "MESH": 
            self.raiseErrorMessage(noMeshMessage)
        if object.mode == "EDIT":
            self.raiseErrorMessage(editMeshMessage)

        vertexGroup = self.getVertexGroup(object, identifier)

        for i, index in enumerate(indices):
            vertexGroup.add([index], weights[i], "REPLACE")
        object.data.update()    
        return object

    def execute_AllSingle(self, object, identifier, weight):
        if object is None: return
        if object.type != "MESH": 
            self.raiseErrorMessage(noMeshMessage)
        if object.mode == "EDIT":
            self.raiseErrorMessage(editMeshMessage)

        vertexGroup = self.getVertexGroup(object, identifier)

        indices = list(range(0, len(object.data.vertices)))
        vertexGroup.add(indices, weight, "REPLACE")
        object.data.update()    
        return object

    def execute_AllList(self, object, identifier, weights):
        if object is None: return
        if object.type != "MESH": 
            self.raiseErrorMessage(noMeshMessage)
        if object.mode == "EDIT":
            self.raiseErrorMessage(editMeshMessage)

        vertexGroup = self.getVertexGroup(object, identifier)

        totalVertices = len(object.data.vertices)    
        for i, weight in enumerate(weights):
            if i >= totalVertices: return 
            vertexGroup.add([i], weight, "REPLACE") 
        object.data.update()
        return object            
     
    def getVertexGroup(self, object, identifier):
        try: return object.vertex_groups[identifier]
        except: return object.vertex_groups.new()
