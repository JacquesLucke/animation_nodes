import bpy
from bpy.props import *
from ... base_types.node import AnimationNode
from . constant_falloff import ConstantFalloff
from ... data_structures cimport AverageSound, BaseFalloff

soundTypeItems = [
    ("AVERAGE", "Average", "", "FORCE_TURBULENCE", 0),
    ("SPECTRUM", "Spectrum", "", "RNDCURVE", 1)
]

averageFalloffTypeItems = [
    ("INDEX_OFFSET", "Index Offset", "", "NONE", 0)
]

class SoundFalloffNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_SoundFalloffNode"
    bl_label = "Sound Falloff"

    soundType = EnumProperty(name = "Sound Type", default = "AVERAGE",
        items = soundTypeItems, update = AnimationNode.refresh)

    averageFalloffType = EnumProperty(name = "Average Falloff Type", default = "INDEX_OFFSET",
        items = averageFalloffTypeItems, update = AnimationNode.refresh)

    useCurrentFrame = BoolProperty(name = "Use Current Frame", default = True,
        update = AnimationNode.refresh)

    def create(self):
        self.newInput("Sound", "Sound", "sound", defaultDrawType = "PROPERTY_ONLY")
        if not self.useCurrentFrame:
            self.newInput("Float", "Frame", "frame")

        if self.soundType == "AVERAGE":
            if self.averageFalloffType == "INDEX_OFFSET":
                self.newInput("Integer", "Offset", "offset", value = 1, minValue = 0)

        self.newOutput("Falloff", "Falloff", "falloff")

    def getExecutionCode(self):
        yield "if sound is not None and sound.type == self.soundType:"
        if self.useCurrentFrame: yield "    _frame = self.nodeTree.scene.frame_current_final"
        else:                    yield "    _frame = frame"

        if self.soundType == "AVERAGE":
            if self.averageFalloffType == "INDEX_OFFSET":
                yield "    falloff = self.execute_Average_IndexOffset(sound, _frame, offset)"

        yield "else: falloff = self.getConstantFalloff(0)"

    def getConstantFalloff(self, value = 0):
        return ConstantFalloff(value)

    def execute_Average_IndexOffset(self, sound, frame, offset):
        return Average_IndexOffset_SoundFalloff(sound, frame, offset)

cdef class Average_IndexOffset_SoundFalloff(BaseFalloff):
    cdef:
        AverageSound sound
        float frame, offsetInverse

    def __cinit__(self, AverageSound sound, float frame, offset):
        self.sound = sound
        self.frame = frame
        self.offsetInverse = 1 / offset if offset != 0 else 0
        self.dataType = "All"

    cdef double evaluate(self, void *object, long index):
        return self.sound.evaluate(self.frame - index * self.offsetInverse)
