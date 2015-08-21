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

    def getExecutionCode(self):
        usedOutputs = self.getUsedOutputsDict()
        lines = []
        if usedOutputs["frame"]: lines.append("frame = bpy.context.scene.frame_current_final")
        if usedOutputs["startFrame"]: lines.append("startFrame = bpy.context.scene.frame_start")
        if usedOutputs["endFrame"]: lines.append("endFrame = bpy.context.scene.frame_end")
        if usedOutputs["frameRate"]: lines.append("frameRate = bpy.context.scene.render.fps")
        return lines
