import bpy
from bpy.props import *
from ... tree_info import keepNodeState
from ... base_types.node import AnimationNode
from ... sockets.info import isBase, toBaseDataType, toListDataType

sliceEndType = [
    ("END_INDEX", "End Index", "", "NONE", 0),
    ("OUTPUT_LENGTH", "Output Length", "", "NONE", 1)]

class SliceListNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_SliceListNode"
    bl_label = "Slice List"

    def assignedTypeChanged(self, context):
        self.generateSockets()

    assignedType = StringProperty(update = assignedTypeChanged)

    def sliceEndTypeChanged(self, context):
        self.generateSockets()

    sliceEndType = EnumProperty(name = "Slice Type", default = "END_INDEX",
        items = sliceEndType, update = sliceEndTypeChanged)

    def create(self):
        self.assignedType = "Float"

    def drawAdvanced(self, layout):
        layout.prop(self, "sliceEndType")
        self.invokeSocketTypeChooser(layout, "assignListDataType",
            socketGroup = "LIST", text = "Change Type", icon = "TRIA_RIGHT")

    def getExecutionCode(self):
        yield "_step = 1 if step == 0 else step"
        if self.sliceEndType == "END_INDEX":
            yield "slicedList = list[start:end:_step]"
        elif self.sliceEndType == "OUTPUT_LENGTH":
            yield "endIndex = max(0, start + _step * length)"
            yield "slicedList = list[start:endIndex:_step]"

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
        self.newInput("Integer", "Start", "start")
        if self.sliceEndType == "END_INDEX":
            self.newInput("Integer", "End", "end")
        elif self.sliceEndType == "OUTPUT_LENGTH":
            self.newInput("Integer", "Length", "length")
        self.newInput("Integer", "Step", "step", value = 1, hide = True)
        self.newOutput(listDataType, "List", "slicedList")
