import bpy
from bpy.props import *
from ... events import propertyChanged
from ... base_types import AnimationNode
from ... data_structures import DoubleList

frameTypes = [
    ("OFFSET", "Offset", ""),
    ("ABSOLUTE", "Absolute", "") ]

soundTypeItems = [
    ("SINGLE", "Single", ""),
    ("SPECTRUM", "Spectrum", "")]

class EvaluateSoundNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_EvaluateSoundNode"
    bl_label = "Evaluate Sound"
    bl_width_default = 185

    def frameTypeChanged(self, context):
        self.inputs["Frame"].hide = False
        propertyChanged()

    def soundTypeChanged(self, context):
        self.outputs["Strength"].hide = self.soundType != "SINGLE"
        self.outputs["Strengths"].hide = self.soundType != "SPECTRUM"

    frameType = EnumProperty(
        name = "Frame Type", default = "OFFSET",
        items = frameTypes, update = frameTypeChanged)

    soundType = EnumProperty(
        name = "Sound Type", default = "SINGLE",
        description = "Changing this has only impact on the UI",
        items = soundTypeItems, update = soundTypeChanged)

    def create(self):
        self.newInput("Sound", "Sound", "sound")
        self.newInput("Float", "Frame", "frame", hide = True)
        self.newOutput("Float", "Strength", "strength")
        self.newOutput("Float List", "Strengths", "strengths", hide = True)

    def draw(self, layout):
        layout.prop(self, "soundType", text = "Type")
        layout.prop(self, "frameType", text = "Frame")

    def drawAdvanced(self, layout):
        layout.prop(bpy.context.scene, "sync_mode")

    def execute(self, sound, frame):
        if sound is None: return 0, DoubleList()
        if self.frameType == "OFFSET":
            frame += self.nodeTree.scene.frame_current_final
        strength = sound.evaluate(frame) if sound.type == "SINGLE" else 0
        strengths = sound.evaluate(frame) if sound.type == "SPECTRUM" else []
        return strength, strengths
