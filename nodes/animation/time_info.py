import bpy
from ... base_types.node import AnimationNode

class TimeInfoNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_TimeInfoNode"
    bl_label = "Time Info"
    searchTags = ["Frame"]
    
    inputNames = {}
    outputNames = { "Frame" : "frame",
                    "Start Frame" : "startFrame",
                    "End Frame" : "endFrame",
                    "Frame Rate" : "frameRate" }
    
    def create(self):
        self.outputs.new("an_FloatSocket", "Frame")
        self.outputs.new("an_FloatSocket", "Start Frame")
        self.outputs.new("an_FloatSocket", "End Frame")
        self.outputs.new("an_FloatSocket", "Frame Rate")
        
    def getExecutionCode(self, usedOutputs):
        codeLines = []
        if usedOutputs["Frame"]: codeLines.append("$frame$ = scene.frame_current_final")
        if usedOutputs["Start Frame"]: codeLines.append("$startFrame$ = scene.frame_start")
        if usedOutputs["End Frame"]: codeLines.append("$endFrame$ = scene.frame_end")
        if usedOutputs["Frame Rate"]: codeLines.append("$frameRate$ = scene.render.fps")
        return "\n".join(codeLines)
