import bpy
from ... base_types.node import AnimationNode

class TimeInfoNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_TimeInfoNode"
    bl_label = "Time Info"
    searchTags = ["Frame"]

    def create(self):
        socket = self.newInput("an_SceneSocket", "Scene", "scene").hide = True
        self.newOutput("an_FloatSocket", "Frame", "frame")
        self.newOutput("an_FloatSocket", "Start Frame", "startFrame").hide = True
        self.newOutput("an_FloatSocket", "End Frame", "endFrame").hide = True
        self.newOutput("an_FloatSocket", "Frame Rate", "frameRate").hide = True

    def edit(self):
        inputSocket = self.inputs[0]
        origin = inputSocket.dataOrigin
        if origin is None: return
        if origin.dataType != "Scene":
            inputSocket.removeLinks()
            inputSocket.hide = True

    def getExecutionCode(self):
        isLinked = self.getLinkedOutputsDict()
        if not any(isLinked.values()): return ""

        lines = []
        lines.append("if scene is not None:")
        if isLinked["frame"]: lines.append("    frame = scene.frame_current_final")
        if isLinked["startFrame"]: lines.append("    startFrame = scene.frame_start")
        if isLinked["endFrame"]: lines.append("    endFrame = scene.frame_end")
        if isLinked["frameRate"]: lines.append("    frameRate = scene.render.fps")
        lines.append("else:")
        lines.append("    frame, startFrame, endFrame, frameRate = 0, 0, 0, 0")
        return lines
