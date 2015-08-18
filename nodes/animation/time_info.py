import bpy
from ... base_types.node import AnimationNode

class TimeInfoNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_TimeInfoNode"
    bl_label = "Time Info"
    searchTags = ["Frame"]

    def create(self):
        self.outputs.new("an_FloatSocket", "Frame", "frame")
        self.outputs.new("an_FloatSocket", "Start Frame", "startFrame")
        self.outputs.new("an_FloatSocket", "End Frame", "endFrame")
        self.outputs.new("an_FloatSocket", "Frame Rate", "frameRate")

    def getExecutionCode(self, usedOutputs):
        lines = []
        if usedOutputs["Frame"]: lines.append("frame = scene.frame_current_final")
        if usedOutputs["Start Frame"]: lines.append("startFrame = scene.frame_start")
        if usedOutputs["End Frame"]: lines.append("endFrame = scene.frame_end")
        if usedOutputs["Frame Rate"]: lines.append("frameRate = scene.render.fps")
        return lines
