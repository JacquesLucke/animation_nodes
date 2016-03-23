import bpy
from bpy.props import *
from ... tree_info import keepNodeState
from ... events import executionCodeChanged
from ... base_types.node import AnimationNode
from ... sockets.info import toIdName, toListIdName, toBaseDataType, isBase, isLimitedList, toGeneralListIdName

class SetListElementNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_SetListElementNode"
    bl_label = "Set List Element"

    def assignedTypeChanged(self, context):
        self.baseIdName = toIdName(self.assignedType)
        self.listIdName = toListIdName(self.assignedType)
        self.generateSockets()

    assignedType = StringProperty(update = assignedTypeChanged)
    baseIdName = StringProperty()
    listIdName = StringProperty()

    clampIndex = BoolProperty(name = "Clamp Index", default = False,
        description = "Clamp the index between the lowest and highest possible index",
        update = executionCodeChanged)

    allowNegativeIndex = BoolProperty(name = "Allow Negative Index",
        description = "-2 means the second last list element",
        update = executionCodeChanged, default = False)

    errorMessage = StringProperty()

    def create(self):
        self.assignedType = "Float"

    def draw(self, layout):
        if self.errorMessage != "":
            layout.label(self.errorMessage, icon = "ERROR")

    def drawAdvanced(self, layout):
        layout.prop(self, "clampIndex")
        layout.prop(self, "allowNegativeIndex")
        self.invokeSocketTypeChooser(layout, "assignListDataType",
            socketGroup = "LIST", text = "Change Type", icon = "TRIA_RIGHT")

    def getExecutionCode(self):
        yield "self.errorMessage = ''"
        if self.isTuple(): yield "_list = list(_list)"
        
        if self.allowNegativeIndex:
            if self.clampIndex:
                yield "if len(_list) != 0: _list[min(max(index, -len(_list)), len(_list) - 1)] = element"
            else:
                yield "if -len(_list) <= index <= len(_list) - 1: _list[index] = element"
        else:
            if self.clampIndex:
                yield "if len(_list) != 0: _list[min(max(index, 0), len(_list) - 1)] = element"
            else:
                yield "if 0 <= index <= len(_list) - 1: _list[index] = element"
        yield "else: self.errorMessage = 'Index out of range'"

    def edit(self):
        dataType = self.getWantedDataType()
        self.assignType(dataType)

    def isTuple(self):
        listInput = self.inputs["List"].dataOrigin
        if listInput is not None:
            if isLimitedList(listInput.bl_idname): return True
        return False

    def getWantedDataType(self):
        listInput = self.inputs["List"].dataOrigin
        elementInput = self.inputs["Element"].dataOrigin
        listOutputs = self.outputs["List"].dataTargets

        if listInput is not None:
            idName = listInput.bl_idname
            if isLimitedList(idName): idName = toGeneralListIdName(idName)
            return toBaseDataType(idName)
        if elementInput is not None: return elementInput.dataType
        if len(listOutputs) == 1: return toBaseDataType(listOutputs[0].dataType)
        return self.inputs["Element"].dataType

    def assignListDataType(self, listDataType):
        self.assignType(toBaseDataType(listDataType))

    def assignType(self, baseDataType):
        if not isBase(baseDataType): return
        if baseDataType == self.assignedType: return
        self.assignedType = baseDataType

    @keepNodeState
    def generateSockets(self):
        self.inputs.clear()
        self.outputs.clear()
        self.inputs.new(self.listIdName, "List", "_list").dataIsModified = True
        self.inputs.new(self.baseIdName, "Element", "element")
        self.inputs.new("an_IntegerSocket", "Index", "index")
        self.outputs.new(self.listIdName, "List", "_list")
