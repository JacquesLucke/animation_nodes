import bpy
from bpy.props import *
from ... sockets.info import toIdName
from ... tree_info import keepNodeState
from ... base_types.node import AnimationNode

class SwitchNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_SwitchNode"
    bl_label = "Switch"

    def assignedTypeChanged(self, context):
        self.socketIdName = toIdName(self.assignedType)
        self.generateSockets()

    assignedType = StringProperty(update = assignedTypeChanged)
    socketIdName = StringProperty()

    def create(self):
        self.assignedType = "Float"

    def drawAdvanced(self, layout):
        self.invokeSocketTypeChooser(layout, "assignType",
            text = "Change Type", icon = "TRIA_RIGHT")

    def edit(self):
        dataType = self.getWantedDataType()
        self.assignType(dataType)

    def getWantedDataType(self):
        for socket in (self.inputs[1], self.inputs[2], self.outputs[0], self.outputs[1]):
            dataOrigin = socket.dataOrigin
            if dataOrigin is not None: return dataOrigin.dataType
        return self.inputs[1].dataType

    def assignType(self, dataType):
        if dataType == self.assignedType: return
        self.assignedType = dataType

    def getExecutionCode(self):
        return ("output = ifTrue if condition else ifFalse",
                "other = ifFalse if condition else ifTrue")

    @keepNodeState
    def generateSockets(self):
        self.inputs.clear()
        self.outputs.clear()

        self.newInput("an_BooleanSocket", "Condition", "condition")
        self.newInput(self.socketIdName, "If True", "ifTrue")
        self.newInput(self.socketIdName, "If False", "ifFalse")
        self.newOutput(self.socketIdName, "Output", "output")
        self.newOutput(self.socketIdName, "Other", "other").hide = True
