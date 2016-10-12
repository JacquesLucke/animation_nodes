import bpy
from bpy.props import *
from ... events import executionCodeChanged
from ... sockets.info import isBase, toBaseDataType, toListDataType
from ... base_types import AnimationNode, AutoSelectListDataType

class GetListElementNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_GetListElementNode"
    bl_label = "Get List Element"
    dynamicLabelType = "HIDDEN_ONLY"

    assignedType = StringProperty(update = AnimationNode.updateSockets, default = "Float")

    clampIndex = BoolProperty(name = "Clamp Index", default = False,
        description = "Clamp the index between the lowest and highest possible index",
        update = executionCodeChanged)

    allowNegativeIndex = BoolProperty(name = "Allow Negative Index",
        description = "-2 means the second last list element",
        update = executionCodeChanged, default = True)

    makeCopy = BoolProperty(name = "Make Copy", default = True,
        description = "Output a copy of the list element to make it independed",
        update = executionCodeChanged)

    def create(self):
        baseDataType = self.assignedType
        listDataType = toListDataType(self.assignedType)

        self.newInput(listDataType, "List", "list")
        self.newInput("Integer", "Index", "index")
        self.newInput(baseDataType, "Fallback", "fallback", hide = True)
        self.newOutput(baseDataType, "Element", "element")

        self.newSocketEffect(AutoSelectListDataType("assignedType", "BASE",
            [(self.inputs[0], "LIST"),
             (self.inputs[2], "BASE"),
             (self.outputs[0], "BASE")]
        ))

    def drawAdvanced(self, layout):
        layout.prop(self, "clampIndex")
        layout.prop(self, "allowNegativeIndex")
        layout.prop(self, "makeCopy")
        self.invokeSocketTypeChooser(layout, "assignListDataType",
            socketGroup = "LIST", text = "Change Type", icon = "TRIA_RIGHT")

    def drawLabel(self):
        if self.inputs["Index"].isUnlinked:
            return "List[{}]".format(self.inputs["Index"].value)
        return "Get List Element"

    def getExecutionCode(self):
        if self.allowNegativeIndex:
            if self.clampIndex:
                yield "if len(list) != 0: element = list[min(max(index, -len(list)), len(list) - 1)]"
                yield "else: element = fallback"
            else:
                yield "element = list[index] if -len(list) <= index < len(list) else fallback"
        else:
            if self.clampIndex:
                yield "if len(list) != 0: element = list[min(max(index, 0), len(list) - 1)]"
                yield "else: element = fallback"
            else:
                yield "element = list[index] if 0 <= index < len(list) else fallback"

        if self.makeCopy:
            socket = self.outputs[0]
            if socket.isCopyable():
                yield "element = " + socket.getCopyExpression().replace("value", "element")

    def assignListDataType(self, listDataType):
        self.assignType(toBaseDataType(listDataType))

    def assignType(self, baseDataType):
        if not isBase(baseDataType): return
        if baseDataType == self.assignedType: return
        self.assignedType = baseDataType
