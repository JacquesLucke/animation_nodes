import bpy
from ... base_types.node import AnimationNode

class TimeInfoNode(bpy.types.Node, AnimationNode):
    bl_idname = "mn_TimeInfoNode"
    bl_label = "Time Info"
    search_tags = ["Frame"]
    
    def create(self):
        self.outputs.new("mn_FloatSocket", "Frame")
        self.outputs.new("mn_FloatSocket", "Start Frame")
        self.outputs.new("mn_FloatSocket", "End Frame")
        self.outputs.new("mn_FloatSocket", "Frame Rate")
        
    def getInputSocketNames(self):
        return {}
        
    def getOutputSocketNames(self):
        return {"Frame" : "frame",
                "Start Frame" : "start_frame",
                "End Frame" : "end_frame",
                "Frame Rate" : "frame_rate"}
        
    def useInLineExecution(self):
        return True
        
    def getInLineExecutionString(self, outputUse):
        codeLines = []
        if outputUse["Frame"]: codeLines.append("$frame$ = scene.frame_current_final")
        if outputUse["Start Frame"]: codeLines.append("$start_frame$ = scene.frame_start")
        if outputUse["End Frame"]: codeLines.append("$end_frame$ = scene.frame_end")
        if outputUse["Frame Rate"]: codeLines.append("$frame_rate$ = scene.render.fps")
        return "\n".join(codeLines)
