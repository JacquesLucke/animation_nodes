import bpy
from ... base_types.node import AnimationNode

class SequenceInfoNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_SequenceInfoNode"
    bl_label = "Sequence Info"

    def create(self):
        self.inputs.new("an_SequenceSocket", "Sequence", "sequence").defaultDrawType = "PROPERTY_ONLY"

        self.outputs.new("an_StringSocket", "Name", "name")
        self.outputs.new("an_StringSocket", "Type", "type")
        self.outputs.new("an_IntegerSocket", "Channel", "channel")
        self.outputs.new("an_IntegerSocket", "Final Duration", "finalDuration")
        self.outputs.new("an_IntegerSocket", "Final Start Frame", "finalStartFrame")
        self.outputs.new("an_IntegerSocket", "Final End Frame", "finalEndFrame")

        self.outputs.new("an_FloatSocket", "Opacity", "opacity")
        self.outputs.new("an_StringSocket", "Blend Type", "blendType")
        self.outputs.new("an_FloatSocket", "Effect Fader", "effectFader")

        self.outputs.new("an_IntegerSocket", "Start Frame", "startFrame")
        self.outputs.new("an_IntegerSocket", "Start Offset", "startOffset")
        self.outputs.new("an_IntegerSocket", "End Offset", "endOffset")
        self.outputs.new("an_IntegerSocket", "Total Duration", "totalDuration")
        self.outputs.new("an_IntegerSocket", "Still Frame Start", "stillFrameStart")
        self.outputs.new("an_IntegerSocket", "Still Frame End", "stillFrameEnd")

        self.outputs.new("an_BooleanSocket", "Lock", "lock")
        self.outputs.new("an_BooleanSocket", "Mute", "mute")
        self.outputs.new("an_BooleanSocket", "Select", "select")
        self.outputs.new("an_FloatSocket", "Speed Factor", "speedFactor")
        self.outputs.new("an_BooleanSocket", "Use Default Fade", "useDefaultFade")
        self.outputs.new("an_BooleanSocket", "Use Linear Modifiers", "useLinearModifiers")

        for socket in self.outputs[6:]:
            socket.hide = True

    def getExecutionCode(self):
        isLinked = self.getLinkedOutputsDict()
        if not any(isLinked.values()): return

        yield "if sequence is not None:"
        if isLinked["opacity"]: yield "    opacity = sequence.blend_alpha"
        if isLinked["blendType"]: yield "    blendType = sequence.blend_type"
        if isLinked["channel"]: yield "    channel = sequence.channel"
        if isLinked["effectFader"]: yield "    effectFader = sequence.effect_fader"

        if isLinked["totalDuration"]: yield "    totalDuration = sequence.frame_duration"
        if isLinked["finalDuration"]: yield "    finalDuration = sequence.frame_final_duration"
        if isLinked["finalStartFrame"]: yield "    finalStartFrame = sequence.frame_final_start"
        if isLinked["finalEndFrame"]: yield "    finalEndFrame = sequence.frame_final_end"
        if isLinked["startOffset"]: yield "    startOffset = sequence.frame_offset_start"
        if isLinked["endOffset"]: yield "    endOffset = sequence.frame_offset_end"
        if isLinked["startFrame"]: yield "    startFrame = sequence.frame_start"
        if isLinked["stillFrameStart"]: yield "    stillFrameStart = sequence.frame_still_start"
        if isLinked["stillFrameEnd"]: yield "    stillFrameEnd = sequence.frame_still_end"

        if isLinked["lock"]: yield "    lock = sequence.lock"
        if isLinked["mute"]: yield "    mute = sequence.mute"
        if isLinked["name"]: yield "    name = sequence.name"
        if isLinked["select"]: yield "    select = sequence.select"
        if isLinked["speedFactor"]: yield "    speedFactor = sequence.speed_factor"
        if isLinked["type"]: yield "    type = sequence.type"
        if isLinked["useDefaultFade"]: yield "    useDefaultFade = sequence.use_default_fade"
        if isLinked["useLinearModifiers"]: yield "    useLinearModifiers = sequence.use_linear_modifiers"

        yield "else:"
        yield "    opacity = 0.0"
        yield "    blendType = ''"
        yield "    channel = 1"
        yield "    effectFader = 0"
        yield "    totalDuration = finalDuration = finalStartFrame = finalEndFrame = 0"
        yield "    startOffset = endOffset = startFrame = 0"
        yield "    stillFrameStart = stillFrameEnd = 0"
        yield "    lock = False"
        yield "    mute = False"
        yield "    name = ''"
        yield "    select = False"
        yield "    speedFactor = 0.0"
        yield "    type = ''"
        yield "    useDefaultFade = False"
        yield "    useLinearModifiers = False"
