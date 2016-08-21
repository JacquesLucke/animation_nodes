import bpy
from bpy.props import *
from . mix_data import getMixCode
from ... events import executionCodeChanged
from ... base_types.node import AnimationNode

class AnimateDataNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_AnimateDataNode"
    bl_label = "Animate Data"
    bl_width_default = 150
    dynamicLabelType = "ALWAYS"

    onlySearchTags = True
    searchTags = [ ("Animate Matrix", {"dataType" : repr("Matrix")}),
                   ("Animate Vector", {"dataType" : repr("Vector")}),
                   ("Animate Float", {"dataType" : repr("Float")}),
                   ("Animate Color", {"dataType" : repr("Color")}),
                   ("Animate Euler", {"dataType" : repr("Euler")}),
                   ("Animate Quaternion", {"dataType" : repr("Quaternion")}) ]

    def dataTypeChanged(self, context):
        self.generateSockets()
        executionCodeChanged()

    dataType = StringProperty(default = "Float", update = dataTypeChanged)

    def create(self):
        self.generateSockets()

    def drawLabel(self):
        return "Animate " + self.inputs[1].dataType

    def generateSockets(self):
        self.inputs.clear()
        self.outputs.clear()

        self.newInput("Float", "Time", "time")
        self.newInput(self.dataType, "Start", "start")
        self.newInput(self.dataType, "End", "end")
        self.newInput("Interpolation", "Interpolation", "interpolation", defaultDrawType = "PROPERTY_ONLY")
        self.newInput("Float", "Duration", "duration", value = 20, minValue = 0.001)

        self.newOutput("Float", "Time", "outTime")
        self.newOutput(self.dataType, "Result", "result")

    def getExecutionCode(self):
        yield "finalDuration = max(duration, 0.0001)"
        yield "influence = max(min(time / finalDuration, 1.0), 0.0)"
        yield "influence = interpolation(influence)"
        yield getMixCode(self.dataType, "start", "end", "influence", "result")
        yield "outTime = time - finalDuration"
