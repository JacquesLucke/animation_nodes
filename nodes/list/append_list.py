import bpy
from ... base_types.node import AnimationNode
from ... tree_info import getOriginSocket, getTargetSockets, keepNodeLinks
from ... sockets.info import toBaseIdName, toListIdName, toIdName, isList, toListDataType

class AppendListNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_AppendListNode"
    bl_label = "Append to List"

    inputNames = { "List" : "list",
                   "Element" : "element" }

    outputNames = { "List" : "list" }

    def create(self):
        self.assignType("Object List")

    def getExecutionCode(self):
        return "$list$ = %list%\n" + \
                "$list$.append(%element%)"

    def edit(self):
        listDataType = self.getWantedDataType()
        self.assignType(listDataType)

    def getWantedDataType(self):
        listInput = getOriginSocket(self.inputs["List"])
        elementInput = getOriginSocket(self.inputs["Element"])
        listOutputs = getTargetSockets(self.outputs["List"])

        if listInput is not None: return listInput.dataType
        if elementInput is not None: return toListDataType(elementInput.bl_idname)
        if len(listOutputs) > 0: return listOutputs[0].dataType
        return self.inputs["List"].dataType

    @keepNodeLinks
    def assignType(self, listDataType = "Object List"):
        if not isList(listDataType): return
        self.generateSockets(listDataType)

    def generateSockets(self, listDataType = "Object List"):
        listIdName = toIdName(listDataType)
        baseIdName = toBaseIdName(listIdName)

        self.inputs.clear()
        self.outputs.clear()
        self.inputs.new(listIdName, "List")
        self.inputs.new(baseIdName, "Element")
        self.outputs.new(listIdName, "List")
