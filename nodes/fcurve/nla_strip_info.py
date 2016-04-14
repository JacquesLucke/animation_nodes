import bpy
from ... base_types.node import AnimationNode

class NLAStripInfoNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_NLAStripInfoNode"
    bl_label = "NLA Strip Info"

    def create(self):
        self.inputs.new("an_GenericSocket", "NLA Strip", "strip")

        self.outputs.new("an_StringSocket", "Strip Name", "stripName")      # use an_NLAStripSocket
        self.outputs.new("an_FloatSocket", "Start Frame", "startFrame")
        self.outputs.new("an_FloatSocket", "End Frame", "endFrame")
        self.outputs.new("an_FloatSocket", "Repeat", "repeat").hide = True
        self.outputs.new("an_FCurveListSocket", "Action FCurves", "fCurves").hide = True

    def getExecutionCode(self):
        isLinked = self.getLinkedOutputsDict()
        if not any(isLinked.values()): return
        
        yield "if getattr(strip, 'type', '') in ['CLIP', 'TRANSITION', 'META', 'SOUND']:" # temp, for generic socket
        #yield "if strip is not None:"      # use this, when we have nla strip sockets
    
        if isLinked["stripName"]: yield "    stripName = strip.name"
        if isLinked["startFrame"]: yield "    startFrame = strip.frame_start"
        if isLinked["endFrame"]: yield "    endFrame = strip.frame_end"
        if isLinked["repeat"]: yield "    repeat = strip.repeat"
        if isLinked["fCurves"]: yield "    fCurves = strip.action.fcurves"
        yield "else: actionName, stripName, startFrame, endFrame, repeat, fCurves = '', '', 0, 0, 1, []"
