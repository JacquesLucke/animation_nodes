import bpy
from ... sockets.info import isBase, toBaseDataType
from ... base_types import AnimationNode, ListTypeSelectorSocket

class InsertListElementNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_InsertListElementNode"
    bl_label = "Insert List Element"

    assignedType: ListTypeSelectorSocket.newProperty(default = "Float")

    def create(self):
        prop = ("assignedType", "BASE")
        self.newInput(ListTypeSelectorSocket(
            "List", "list", "LIST", prop, dataIsModified = True))
        self.newInput(ListTypeSelectorSocket(
            "Element", "element", "BASE", prop, dataIsModified = True))
        self.newInput("Integer", "Index", "index")
        self.newOutput(ListTypeSelectorSocket(
            "List", "list", "LIST", prop))

    def drawAdvanced(self, layout):
        self.invokeSelector(layout, "DATA_TYPE", "assignListDataType",
            dataTypes = "LIST", text = "Change Type", icon = "TRIA_RIGHT")

    def getExecutionCode(self, required):
        return "list.insert(index, element)"

    def assignListDataType(self, listDataType):
        self.assignType(toBaseDataType(listDataType))

    def assignType(self, baseDataType):
        if not isBase(baseDataType): return
        if baseDataType == self.assignedType: return
        self.assignedType = baseDataType
        self.refresh()
