import bpy
from bpy.props import *
from . mix_data import getMixCode
from ... sockets.info import toIdName
from ... events import executionCodeChanged
from ... base_types.node import AnimationNode

class AnimateDataNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_AnimateDataNode"
    bl_label = "Animate Data"

    onlySearchTags = True
    searchTags = [ ("Animate Matrix", {"dataType" : repr("Matrix")}),
                   ("Animate Vector", {"dataType" : repr("Vector")}),
                   ("Animate Float", {"dataType" : repr("Float")}),
                   ("Animate Color", {"dataType" : repr("Color")}) ]

    def dataTypeChanged(self, context):
        self.generateSockets()
        executionCodeChanged()

    dataType = StringProperty(default = "Float", update = dataTypeChanged)

    def create(self):
        self.width = 150
        self.generateSockets()

    def generateSockets(self):
        self.inputs.clear()
        self.outputs.clear()

        idName = toIdName(self.dataType)
        self.inputs.new("an_FloatSocket", "Time", "time")
        self.inputs.new(idName, "Start", "start")
        self.inputs.new(idName, "End", "end")
        self.inputs.new("an_InterpolationSocket", "Interpolation", "interpolation").defaultDrawType = "PROPERTY_ONLY"
        socket = self.inputs.new("an_FloatSocket", "Duration", "duration")
        socket.minValue = 0.0001
        socket.value = 20

        self.outputs.new("an_FloatSocket", "Time", "outTime")
        self.outputs.new(idName, "Result", "result")

    def getExecutionCode(self):
        yield "finalDuration = max(duration, 0.0001)"
        yield "influence = max(min(time / duration, 1.0), 0.0)"
        yield "influence = interpolation[0](influence, interpolation[1])"
        yield getMixCode(self.dataType, "start", "end", "influence", "result")
        yield "outTime = time - duration"
