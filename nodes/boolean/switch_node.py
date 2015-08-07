import bpy
from bpy.props import *
from ... sockets.info import toIdName
from ... tree_info import keepNodeLinks
from ... base_types.node import AnimationNode

class SwitchNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_SwitchNode"
    bl_label = "Switch"

    inputNames = { "Condition" : "condition",
                   "If True" : "ifTrue",
                   "If False" : "ifFalse" }

    outputNames = { "Output" : "output",
                    "Other" : "other" }

    def assignedTypeChanged(self, context):
        self.socketIdName = toIdName(self.assignedType)
        self.generateSockets()

    assignedType = StringProperty(update = assignedTypeChanged)
    socketIdName = StringProperty()

    def create(self):
        self.assignedType = "Float"

    def edit(self):
        dataType = self.getWantedDataType()
        self.assignType(dataType)

    def getWantedDataType(self):
        for socket in (self.inputs[1], self.inputs[2], self.outputs[0], self.outputs[1]):
            dataOrigin = socket.dataOriginSocket
            if dataOrigin is not None: return dataOrigin.dataType
        return self.inputs[1].dataType

    def assignType(self, dataType):
        if dataType == self.assignedType: return
        self.assignedType = dataType

    def getExecutionCode(self):
        return "$output$ = %ifTrue% if %condition% else %ifFalse%" + "\n" + \
               "$other$ = %ifFalse% if %condition% else %ifTrue%"

    @keepNodeLinks
    def generateSockets(self):
        self.inputs.clear()
        self.outputs.clear()
        
        self.inputs.new("an_BooleanSocket", "Condition")
        self.inputs.new(self.socketIdName, "If True")
        self.inputs.new(self.socketIdName, "If False")
        self.outputs.new(self.socketIdName, "Output")
        self.outputs.new(self.socketIdName, "Other").hide = True
