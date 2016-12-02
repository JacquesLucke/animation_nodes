import bpy
from bpy.props import *
from ... tree_info import keepNodeLinks
from ... base_types.node import AnimationNode
from ... sockets.info import toIdName

class ConvertNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_ConvertNode"
    bl_label = "Convert"
    bl_width = 100

    def assignedTypeChanged(self, context):
        self.recreateOutputSocket()

    lastCorrectionType = IntProperty()

    def create(self):
        self.newInput("Generic", "Old", "old", dataIsModified = True)
        self.recreateOutputSocket("Generic")
        self.width_hidden = 45

    def drawAdvanced(self, layout):
        self.invokeSocketTypeChooser(layout, "assignOutputType",
            socketGroup = "ALL", text = "Change Type", icon = "TRIA_RIGHT")

    def edit(self):
        socket = self.outputs[0]
        targets = socket.dataTargets
        if len(targets) == 1:
            target = targets[0]
            if target.dataType != "Generic":
                self.assignOutputType(target.dataType)

    def assignOutputType(self, dataType):
        self.recreateOutputSocket(dataType)

    @keepNodeLinks
    def recreateOutputSocket(self, dataType):
        self.outputs.clear()
        self.newOutput(dataType, "New", "new")

    def getExecutionCode(self):
        yield "new, self.lastCorrectionType = self.outputs[0].correctValue(old)"
