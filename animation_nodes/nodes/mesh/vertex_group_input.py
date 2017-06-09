import bpy
from bpy.props import *
from ... events import propertyChanged
from ... base_types import VectorizedNode
from ... data_structures import DoubleList

modeItems = [
    ("ALL", "All", "Get weight of every vertex", "NONE", 0),
    ("INDEX", "Index", "Get weight of a specific vertex", "NONE", 1)
]

groupIdentifierTypeItems = [
    ("INDEX", "Index", "Get vertex group based on the index", "NONE", 0),
    ("NAME", "Name", "Get vertex group based on the name", "NONE", 1)
]

class VertexGroupInputNode(bpy.types.Node, VectorizedNode):
    bl_idname = "an_VertexGroupInputNode"
    bl_label = "Vertex Group Input"

    mode = EnumProperty(name = "Mode", default = "ALL",
        items = modeItems, update = VectorizedNode.refresh)

    groupIdentifierType = EnumProperty(name = "Group Identifier Type", default = "INDEX",
        items = groupIdentifierTypeItems, update = VectorizedNode.refresh)

    useIndexList = VectorizedNode.newVectorizeProperty()

    def create(self):
        self.newInput("Object", "Object", "object", defaultDrawType = "PROPERTY_ONLY")

        if self.groupIdentifierType == "INDEX":
            self.newInput("Integer", "Group Index", "groupIndex")
        elif self.groupIdentifierType == "NAME":
            self.newInput("Text", "Name", "name")

        if self.mode == "INDEX":
            self.newVectorizedInput("Integer", "useIndexList",
                ("Index", "index"), ("Indices", "indices"))
            self.newVectorizedOutput("Float", "useIndexList",
                ("Weight", "weight"), ("Weights", "weights"))
        elif self.mode == "ALL":
            self.newOutput("Float List", "Weights", "weights")

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
        try: return self.getVertexGroup(identifier).weight(index)
        except: return 0

    def execute_Indices(self, object, identifier, indices):
        vertexGroup = self.getVertexGroup(object, identifier)
        if vertexGroup is None:
            return DoubleList()

        weights = DoubleList(length = len(indices))
        getWeight = vertexGroup.weight

        for i, index in enumerate(indices):
            try: weights[i] = getWeight(index)
            except: weights[i] = 0
        return weights

    def execute_All(self, object, identifier):
        if getattr(object, "type", "") != "MESH":
            return DoubleList()

        vertexGroup = self.getVertexGroup(object, identifier)
        if vertexGroup is None:
            return DoubleList()

        vertexAmount = len(object.data.vertices)
        weights = DoubleList(length = vertexAmount)
        getWeight = vertexGroup.weight

        for i in range(vertexAmount):
            try: weights[i] = getWeight(i)
            except: weights[i] = 0
        return weights

    def getVertexGroup(self, object, identifier):
        try: return object.vertex_groups[identifier]
        except: return None
