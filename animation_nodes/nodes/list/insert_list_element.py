import bpy
from ... sockets.info import isBase, toBaseDataType
from ... base_types import AnimationNode, ListTypeSelectorSocket, VectorizedSocket

class InsertListElementNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_InsertListElementNode"
    bl_label = "Insert List Element"

    assignedType: ListTypeSelectorSocket.newProperty(default = "Float")
    useList: VectorizedSocket.newProperty()

    def create(self):
        prop = ("assignedType", "BASE")
        print(self.assignedType)
        self.newInput(ListTypeSelectorSocket(
            "List", "list", "LIST", prop, dataIsModified = True))
        self.newInput(VectorizedSocket(str(self.assignedType), "useList", ("Element", "element"), ("Elements", "elements")))
        self.newInput("Integer", "Index", "index")
        self.newOutput(ListTypeSelectorSocket(
            "List", "list", "LIST", prop))

    def drawAdvanced(self, layout):
        self.invokeSelector(layout, "DATA_TYPE", "assignListDataType",
            dataTypes = "LIST", text = "Change Type", icon = "TRIA_RIGHT")

    def getExecutionCode(self, required):
        if not self.useList:
            yield "list.insert(index, element)"
        else:
            yield "temp = list"
            yield "list = list[:index]"
            yield "list.extend(elements)"
            yield "list.extend(temp[index:])"

    def assignListDataType(self, listDataType):
        self.assignType(toBaseDataType(listDataType))

    def assignType(self, baseDataType):
        if not isBase(baseDataType): return
        if baseDataType == self.assignedType: return
        self.assignedType = baseDataType
        self.refresh()
