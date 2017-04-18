import bpy
from bpy.props import *
from ... base_types import AnimationNode, AutoSelectDataType
from ... sockets.info import toIdName

class ConvertNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_ConvertNode"
    bl_label = "Convert"
    bl_width = 100

    dataType = StringProperty(default = "Generic", update = AnimationNode.refresh)
    lastCorrectionType = IntProperty()

    def setup(self):
        self.width_hidden = 45

    def create(self):
        self.newInput("Generic", "Old", "old", dataIsModified = True)
        self.newOutput(self.dataType, "New", "new")
        self.newSocketEffect(AutoSelectDataType(
            "dataType", [self.outputs[0]], ignore = {"Generic"}))

    def drawAdvanced(self, layout):
        self.invokeSelector(layout, "DATA_TYPE", "assignOutputType",
            text = "Change Type", icon = "TRIA_RIGHT")

    def assignOutputType(self, dataType):
        if self.dataType != dataType:
            self.dataType = dataType

    def getExecutionCode(self):
        yield "new, self.lastCorrectionType = self.outputs[0].correctValue(old)"
