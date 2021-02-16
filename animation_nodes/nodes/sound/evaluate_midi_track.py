import bpy
from bpy.props import *
from ... base_types import AnimationNode

evaluationTypeItems = (
    ("SINGLE", "Single", "", "NONE", 0),
    ("ALL", "All", "", "NONE", 1),
)

class EvaluateMIDITrackNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_EvaluateMIDITrackNode"
    bl_label = "Evaluate MIDI Track"

    evaluationType: EnumProperty(name = "Evaluation Type", default = "SINGLE",
        items = evaluationTypeItems, update = AnimationNode.refresh)

    def draw(self, layout):
        layout.prop(self, "evaluationType", text = "")

    def create(self):
        self.newInput("MIDI Track", "Track", "track")
        self.newInput("Float", "Frame", "frame")
        self.newInput("Integer", "Channel", "channel").setRange(0, 15)
        if self.evaluationType == "SINGLE":
            self.newInput("Integer", "Note Number", "noteNumber").setRange(0, 127)
        self.newInput("Float", "Attack Time", "attackTime", value = 0.01)
        self.newInput("Interpolation", "Attack Interpolation",
                "attackInterpolation", defaultDrawType = "PROPERTY_ONLY")
        self.newInput("Float", "Release Time", "releaseTime", value = 0.05)
        self.newInput("Interpolation", "Release Interpolation",
                "releaseInterpolation", defaultDrawType = "PROPERTY_ONLY")
        self.newInput("Scene", "Scene", "scene", hide = True)

        if self.evaluationType == "SINGLE":
            self.newOutput("Float", "Note Value", "noteValue")
        else:
            self.newOutput("Float List", "Note Values", "noteValues")

    def getExecutionCode(self, required):
        yield "time = frame / AN.utils.scene.getFPS(scene)"
        if self.evaluationType == "SINGLE":
            yield ("noteValue = track.evaluate(time, channel, noteNumber,"
                   "attackTime, attackInterpolation, releaseTime, releaseInterpolation)")
        else:
            yield ("noteValues = DoubleList.fromValues(track.evaluateAll(time, channel,"
                   "attackTime, attackInterpolation, releaseTime, releaseInterpolation))")
