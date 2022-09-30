import bpy
from bpy.props import *
from ... events import propertyChanged
from ... data_structures import VirtualDoubleList
from ... base_types import AnimationNode, VectorizedSocket

modeItems = [
    ("ALL", "All", "Set weight of every vertex", "NONE", 0),
    ("INDEX", "Index", "Set weight of a specific vertex", "NONE", 1)
]

groupIdentifierTypeItems = [
    ("INDEX", "Index", "Get vertex group based on the index", "NONE", 0),
    ("NAME", "Name", "Get vertex group based on the name", "NONE", 1)
]

class SetVertexWeightNode(AnimationNode, bpy.types.Node):
    bl_idname = "an_SetVertexWeightNode"
    bl_label = "Set Vertex Weight"
    errorHandlingType = "EXCEPTION"

    mode: EnumProperty(name = "Mode", default = "ALL",
        items = modeItems, update = AnimationNode.refresh)

    groupIdentifierType: EnumProperty(name = "Group Identifier Type", default = "INDEX",
        items = groupIdentifierTypeItems, update = AnimationNode.refresh)

    useIndexList: VectorizedSocket.newProperty()
    useWeightsList: VectorizedSocket.newProperty()
 
    def create(self):
        self.newInput("Object", "Object", "object", defaultDrawType = "PROPERTY_ONLY")

        if self.groupIdentifierType == "INDEX":
            self.newInput("Integer", "Group Index", "groupIndex")
        elif self.groupIdentifierType == "NAME":
            self.newInput("Text", "Name", "groupName")

        if self.mode == "INDEX":
            self.newInput(VectorizedSocket("Integer", "useIndexList",
                ("Index", "index"), ("Indices", "indices")))
                
        self.newInput(VectorizedSocket("Float", ["useWeightsList", "useIndexList"],
                ("Weight", "weight"), ("Weights", "weights")))
        
        self.newOutput("Object", "Object", "object")

    def draw(self, layout):
        layout.prop(self, "mode", text = "")

    def drawAdvanced(self, layout):
        layout.prop(self, "groupIdentifierType", text = "Type")

    def getExecutionFunctionName(self):
        if self.mode == "INDEX":
            if self.useIndexList:
                if self.useWeightsList:
                    return "execute_Indices_WeightsList"
                else:
                    return "execute_Indices_SingleWeight"
            else:
                return "execute_Index_Weight"

        elif self.mode == "ALL":
            if self.useWeightsList:
                return "execute_All_WeightsList"
            else:
                return "execute_All_SingleWeight"

    def execute_Index_Weight(self, object, identifier, index, weight):
        if object is None: return
        vertexGroup = self.getVertexGroup(object, identifier)

        vertexGroup.add([index], weight, "REPLACE")
        object.data.update()    
        return object

    def execute_Indices_SingleWeight(self, object, identifier, indices, weight):
        if object is None: return
        vertexGroup = self.getVertexGroup(object, identifier)

        vertexGroup.add(indices, weight, "REPLACE")
        object.data.update()    
        return object

    def execute_Indices_WeightsList(self, object, identifier, indices, weights):
        if object is None: return
        vertexGroup = self.getVertexGroup(object, identifier)

        weights = VirtualDoubleList.create(weights, 0)
        for i, index in enumerate(indices):
            vertexGroup.add([index], weights[i], "REPLACE")
        object.data.update()    
        return object

    def execute_All_SingleWeight(self, object, identifier, weight):
        if object is None: return
        vertexGroup = self.getVertexGroup(object, identifier)

        indices = list(range(len(object.data.vertices)))

        vertexGroup.add(indices, weight, "REPLACE")
        object.data.update()    
        return object

    def execute_All_WeightsList(self, object, identifier, weights):
        if object is None: return
        vertexGroup = self.getVertexGroup(object, identifier)

        weights = VirtualDoubleList.create(weights, 0)
        for i in range(len(object.data.vertices)):
            vertexGroup.add([i], weights[i], "REPLACE") 
        object.data.update()
        return object            

    def getVertexGroup(self, object, identifier):
        if object.type != "MESH": 
            self.raiseErrorMessage("No mesh object.")
        
        if object.mode == "EDIT":
            self.raiseErrorMessage("Object is not in object mode.")

        try: return object.vertex_groups[identifier]
        except: self.raiseErrorMessage("Group is not found.")
