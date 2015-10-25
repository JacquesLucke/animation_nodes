import bpy
from bpy.utils import smpte_from_frame
from ... base_types.node import AnimationNode

class TimecodeGeneratorNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_TimecodeGeneratorNode"
    bl_label = "Timecode Generator"

    def create(self):
        self.inputs.new("an_FloatSocket", "Frame", "frame")
        socket = self.inputs.new("an_FloatSocket", "Frame Rate", "frameRate")
        socket.value = 25
        socket.minValue = 0
        self.outputs.new("an_StringSocket", "Timecode", "timecode")

    def execute(self, frame, frameRate):
        if frameRate > 0:
            return smpte_from_frame(frame, fps = frameRate)
        return smpte_from_frame(0)
