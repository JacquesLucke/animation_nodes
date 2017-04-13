import bpy
from bpy.props import *
from ... base_types import AnimationNode

originTypeItems = [
    ("Edge Indices", "Edge Indices", "", "NONE", 0),
    ("Polygon Indices", "Polygon Indices", "", "NONE", 1),
    ("Float List", "Float List", "", "NONE", 2)]

class ConvertToIntegerListNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_ConvertToIntegerListNode"
    bl_label = "Convert to Integer List"

    originType = EnumProperty(name = "Origin Type", default = "Float List",
        items = originTypeItems, update = AnimationNode.refresh)

    def setup(self):
        self.width_hidden = 45

    def create(self):
        self.newInput(self.originType, self.originType, "inList")
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
        yield "integerList = LongList.fromValues(inList)"
