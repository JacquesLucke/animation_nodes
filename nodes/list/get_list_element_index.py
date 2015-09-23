import bpy
from bpy.props import *
from ... tree_info import keepNodeLinks
from ... events import executionCodeChanged
from ... base_types.node import AnimationNode
from ... sockets.info import getBaseDataTypeItems, toIdName, toListIdName, isBase, toBaseDataType

class GetListElementIndexNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_GetListElementIndexNode"
    bl_label = "Get Element Index"    #Search List Element ?
    
    def assignedTypeChanged(self, context):
        self.baseIdName = toIdName(self.assignedType)
        self.listIdName = toListIdName(self.assignedType)
        self.generateSockets()

    assignedType = StringProperty(update = assignedTypeChanged)
    baseIdName = StringProperty()
    listIdName = StringProperty()
    
    def create(self):
        self.assignedType = "Float" 
        self.outputs.new("an_IntegerSocket", "First Index", "firstIndex")
        self.outputs.new("an_IntegerListSocket", "All Indices", "allIndices")
        self.outputs.new("an_IntegerSocket", "Occurrences", "occurrences")
        
    def drawAdvanced(self, layout):
        self.invokeSocketTypeChooser(layout, "assignListDataType",
            socketGroup = "LIST", text = "Change Type", icon = "TRIA_RIGHT")
        
    def getExecutionCode(self):
        isLinked = self.getLinkedOutputsDict()
        if not any(isLinked.values()): return ""
        
        lines = []
        lines.append("allIndices = [i for i, element in enumerate(list) if element == search]")
        if isLinked["firstIndex"]: lines.append("firstIndex = allIndices[0] if len(allIndices) > 0 else -1")
        if isLinked["occurrences"]: lines.append("occurrences = len(allIndices)")

        return lines
    
    def edit(self):
        baseDataType = self.getWantedDataType()
        self.assignType(baseDataType)

    def getWantedDataType(self):
        listInput = self.inputs["List"].dataOrigin
        elementInput = self.inputs["Search"].dataOrigin

        if listInput is not None: return toBaseDataType(listInput.bl_idname)
        if elementInput is not None: return elementInput.dataType
        return self.inputs["Search"].dataType

    def assignListDataType(self, listDataType):
        self.assignType(toBaseDataType(listDataType))

    def assignType(self, baseDataType):
        if not isBase(baseDataType): return
        if baseDataType == self.assignedType: return
        self.assignedType = baseDataType

    @keepNodeLinks
    def generateSockets(self):
        self.inputs.clear()
        self.inputs.new(self.listIdName, "List", "list").dataIsModified  = True
        self.inputs.new(self.baseIdName, "Search", "search").dataIsModified = True
