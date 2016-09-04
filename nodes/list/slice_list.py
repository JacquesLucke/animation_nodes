import bpy
from bpy.props import *
from ... tree_info import keepNodeState
from ... base_types import AnimationNode
from ... sockets.info import isBase, toBaseDataType, toListDataType

sliceEndType = [
    ("END_INDEX", "Index", "", "NONE", 0),
    ("OUTPUT_LENGTH", "Length", "", "NONE", 1)]

class SliceListNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_SliceListNode"
    bl_label = "Slice List"
    bl_width_default = 170

    def settingChanged(self, context):
        self.generateSockets()

    assignedType = StringProperty(update = settingChanged)

    useStart = BoolProperty(name = "Start", default = True,
        update = settingChanged)
    useEnd = BoolProperty(name = "End", default = True,
        update = settingChanged)
    useStep = BoolProperty(name = "Step", default = False,
        update = settingChanged)

    sliceEndType = EnumProperty(name = "Slice Type", default = "END_INDEX",
        items = sliceEndType, update = settingChanged)

    def create(self):
        self.assignedType = "Float"

    def draw(self, layout):
        col = layout.column()
        row = col.row(align = True)
        row.prop(self, "useStart", expand = True, icon = "TRIA_RIGHT")
        row.prop(self, "useEnd", expand = True, icon = "TRIA_LEFT")
        row.prop(self, "useStep", expand = True, icon = "ARROW_LEFTRIGHT")
        if self.useEnd:
            col.prop(self, "sliceEndType", text = "End")

    def drawAdvanced(self, layout):
        self.invokeSocketTypeChooser(layout, "assignListDataType",
            socketGroup = "LIST", text = "Change Type", icon = "TRIA_RIGHT")

    def getExecutionCode(self):
        if self.useStart: yield "_start = start"
        else:             yield "_start = 0"

        if self.useStep: yield "_step = 1 if step == 0 else step"
        else:            yield "_step = 1"

        if self.useEnd:
            if self.sliceEndType == "END_INDEX":
                yield "_end = end"
            elif self.sliceEndType == "OUTPUT_LENGTH":
                yield "_end = max(0, _start + _step * length)"

        elements = ["_start" if self.useStart else "",
                    "_end" if self.useEnd else "",
                    "_step" if self.useStep else ""]
        yield "slicedList = list[{}]".format(":".join(elements))

    def edit(self):
        baseDataType = self.getWantedDataType()
        self.assignType(baseDataType)

    def getWantedDataType(self):
        listInput = self.inputs["List"].dataOrigin
        listOutputs = self.outputs["List"].dataTargets

        if listInput is not None: return toBaseDataType(listInput.bl_idname)
        if len(listOutputs) == 1: return toBaseDataType(listOutputs[0].bl_idname)
        return toBaseDataType(self.inputs["List"].bl_idname)

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

        listDataType = toListDataType(self.assignedType)
        self.newInput(listDataType, "List", "list", dataIsModified  = True)
        if self.useStart:
            self.newInput("Integer", "Start", "start")
        if self.useEnd:
            if self.sliceEndType == "END_INDEX":
                self.newInput("Integer", "End", "end")
            elif self.sliceEndType == "OUTPUT_LENGTH":
                self.newInput("Integer", "Length", "length")
        if self.useStep:
            self.newInput("Integer", "Step", "step", value = 1)
        self.newOutput(listDataType, "List", "slicedList")
