import bpy
from bpy.props import *
from ... events import propertyChanged
from ... base_types.node import AnimationNode

frameTypes = [
    ("OFFSET", "Offset", ""),
    ("ABSOLUTE", "Absolute", "") ]

class EvaluateSoundNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_EvaluateSoundNode"
    bl_label = "Evaluate Sound"

    def frameTypeChanged(self, context):
        self.inputs["Frame"].hide = False
        propertyChanged()

    frameType = EnumProperty(
        name = "Frame Type", default = "OFFSET",
        items = frameTypes, update = frameTypeChanged)

    def create(self):
        self.width = 175
        self.inputs.new("an_SoundSocket", "Sound", "sound")
        self.inputs.new("an_FloatSocket", "Frame", "frame").hide = True
        self.outputs.new("an_FloatSocket", "Strength", "strength")

    def draw(self, layout):
        layout.prop(self, "frameType", text = "Type")

    def drawAdvanced(self, layout):
        layout.prop(bpy.context.scene, "sync_mode")

    def execute(self, sound, frame):
        if sound is None: return 0
        if sound.type != "Single": return 0
        if self.frameType == "OFFSET":
            frame += bpy.context.scene.frame_current_final
        return sound.evaluate(frame)
