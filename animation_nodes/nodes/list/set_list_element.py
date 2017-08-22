import bpy
from bpy.props import *
from ... events import executionCodeChanged
from ... sockets.info import toBaseDataType, isBase
from ... base_types import AnimationNode, ListTypeSelectorSocket

class SetListElementNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_SetListElementNode"
    bl_label = "Set List Element"

    assignedType = ListTypeSelectorSocket.newProperty(default = "Float")

    clampIndex = BoolProperty(name = "Clamp Index", default = False,
        description = "Clamp the index between the lowest and highest possible index",
        update = executionCodeChanged)

    allowNegativeIndex = BoolProperty(name = "Allow Negative Index",
        description = "-2 means the second last list element",
        update = executionCodeChanged, default = False)

    errorMessage = StringProperty()

    def create(self):
        prop = ("assignedType", "BASE")
        self.newInput(ListTypeSelectorSocket(
            "List", "list", "LIST", prop, dataIsModified = True))
        self.newInput(ListTypeSelectorSocket(
            "Element", "element", "BASE", prop))
        self.newInput("Integer", "Index", "index")

        self.newOutput(ListTypeSelectorSocket(
            "List", "list", "LIST", prop))

    def draw(self, layout):
        if self.errorMessage != "":
            layout.label(self.errorMessage, icon = "ERROR")

    def drawAdvanced(self, layout):
        layout.prop(self, "clampIndex")
        layout.prop(self, "allowNegativeIndex")
        self.invokeSelector(layout, "DATA_TYPE", "assignListDataType",
            dataTypes = "LIST", text = "Change Type", icon = "TRIA_RIGHT")

    def getExecutionCode(self, required):
        yield "self.errorMessage = ''"
        if self.allowNegativeIndex:
            if self.clampIndex:
                yield "if len(list) != 0: list[min(max(index, -len(list)), len(list) - 1)] = element"
            else:
                yield "if -len(list) <= index <= len(list) - 1: list[index] = element"
        else:
            if self.clampIndex:
                yield "if len(list) != 0: list[min(max(index, 0), len(list) - 1)] = element"
            else:
                yield "if 0 <= index <= len(list) - 1: list[index] = element"
        yield "else: self.errorMessage = 'Index out of range'"

    def assignListDataType(self, listDataType):
        self.assignType(toBaseDataType(listDataType))

    def assignType(self, baseDataType):
        if not isBase(baseDataType): return
        if baseDataType == self.assignedType: return
        self.assignedType = baseDataType
        self.refresh()
