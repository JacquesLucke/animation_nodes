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
        isLinked = self.getLinkedOutputsDict()
        lines = []
        if isLinked["frame"]: lines.append("frame = bpy.context.scene.frame_current_final")
        if isLinked["startFrame"]: lines.append("startFrame = bpy.context.scene.frame_start")
        if isLinked["endFrame"]: lines.append("endFrame = bpy.context.scene.frame_end")
        if isLinked["frameRate"]: lines.append("frameRate = bpy.context.scene.render.fps")
        return lines
