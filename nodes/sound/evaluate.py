import bpy
from bpy.props import *
from ... events import propertyChanged
from ... base_types.node import AnimationNode

frameTypes = [
    ("OFFSET", "Offset", ""),
    ("ABSOLUTE", "Absolute", "") ]

soundTypeItems = [
    ("SINGLE", "Single", ""),
    ("EQUALIZER", "Equalizer", "")]

class EvaluateSoundNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_EvaluateSoundNode"
    bl_label = "Evaluate Sound"

    def frameTypeChanged(self, context):
        self.inputs["Frame"].hide = False
        propertyChanged()

    def soundTypeChanged(self, context):
        self.outputs["Strength"].hide = self.soundType != "SINGLE"
        self.outputs["Strengths"].hide = self.soundType != "EQUALIZER"

    frameType = EnumProperty(
        name = "Frame Type", default = "OFFSET",
        items = frameTypes, update = frameTypeChanged)

    soundType = EnumProperty(
        name = "Sound Type", default = "SINGLE",
        description = "Changing this has only impact on the UI",
        items = soundTypeItems, update = soundTypeChanged)

    def create(self):
        self.width = 175
        self.inputs.new("an_SoundSocket", "Sound", "sound")
        self.inputs.new("an_FloatSocket", "Frame", "frame").hide = True
        self.outputs.new("an_FloatSocket", "Strength", "strength")
        self.outputs.new("an_FloatListSocket", "Strengths", "strengths").hide = True

    def draw(self, layout):
        layout.prop(self, "soundType", text = "Type")
        layout.prop(self, "frameType", text = "Frame")

    def drawAdvanced(self, layout):
        layout.prop(bpy.context.scene, "sync_mode")

    def execute(self, sound, frame):
        if sound is None: return 0, []
        if self.frameType == "OFFSET":
            frame += bpy.context.scene.frame_current_final
        strength = sound.evaluate(frame) if sound.type == "SINGLE" else 0
        strengths = sound.evaluate(frame) if sound.type == "EQUALIZER" else []
        return strength, strengths
