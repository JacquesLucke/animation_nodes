import bpy
from bpy.props import *
from ... tree_info import keepNodeState
from ... base_types.node import AnimationNode

originTypeItems = [
    ("Edge Indices", "Edge Indices", "", "NONE", 0),
    ("Polygon Indices", "Polygon Indices", "", "NONE", 1),
    ("Float List", "Float List", "", "NONE", 2)]

class ConvertToIntegerListNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_ConvertToIntegerListNode"
    bl_label = "Convert to Integer List"

    def originTypeChanged(self, context):
        self.recreateInput()

    originType = EnumProperty(name = "Origin Type", default = "Float List",
        items = originTypeItems, update = originTypeChanged)

    def create(self):
        self.recreateInput()
        self.newOutput("Integer List", "Integer List", "integerList")

    def drawAdvanced(self, layout):
        layout.prop(self, "originType")

    def edit(self):
        originSocket = self.inputs[0].dataOrigin
        if originSocket is not None:
            if originSocket.dataType in ("Edge Indices", "Polygon Indices", "Float List"):
                self.setOriginType(originSocket.dataType)

    def setOriginType(self, dataType):
        if dataType != self.originType:
            self.originType = dataType

    def getExecutionCode(self):
        if "Indices" in self.originType:
            yield "integerList = LongLongList.fromValues(inList)"
        elif self.originType == "Float List":
            yield "integerList = algorithms.list_conversion.DoubleList_to_LongLongList(inList)"

    @keepNodeState
    def recreateInput(self):
        self.inputs.clear()
        self.newInput(self.originType, self.originType, "inList")
