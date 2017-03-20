import bpy
from bpy.props import *
from libc.limits cimport LONG_MAX
from ... base_types.node import AnimationNode
from . constant_falloff import ConstantFalloff
from ... data_structures cimport AverageSound, BaseFalloff, DoubleList, Interpolation

soundTypeItems = [
    ("AVERAGE", "Average", "", "FORCE_TURBULENCE", 0),
    ("SPECTRUM", "Spectrum", "", "RNDCURVE", 1)
]

averageFalloffTypeItems = [
    ("INDEX_OFFSET", "Index Offset", "", "NONE", 0)
]

spectrumFalloffTypeItems = [
    ("INDEX_FREQUENCY", "Index Frequency", "NONE", 0)
]

class SoundFalloffNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_SoundFalloffNode"
    bl_label = "Sound Falloff"

    soundType = EnumProperty(name = "Sound Type", default = "AVERAGE",
        items = soundTypeItems, update = AnimationNode.refresh)

    averageFalloffType = EnumProperty(name = "Average Falloff Type", default = "INDEX_OFFSET",
        items = averageFalloffTypeItems, update = AnimationNode.refresh)

    spectrumFalloffType = EnumProperty(name = "Spectrum Falloff Type", default = "INDEX_FREQUENCY",
        items = spectrumFalloffTypeItems, update = AnimationNode.refresh)

    useCurrentFrame = BoolProperty(name = "Use Current Frame", default = True,
        update = AnimationNode.refresh)

    def create(self):
        self.newInput("Sound", "Sound", "sound", defaultDrawType = "PROPERTY_ONLY")
        if not self.useCurrentFrame:
            self.newInput("Float", "Frame", "frame")

        if self.soundType == "AVERAGE":
            if self.averageFalloffType == "INDEX_OFFSET":
                self.newInput("Integer", "Offset", "offset", value = 1, minValue = 0)
        elif self.soundType == "SPECTRUM":
            if self.spectrumFalloffType == "INDEX_FREQUENCY":
                self.newInput("Integer", "Length", "length", value = 10, minValue = 1)
                self.newInput("Interpolation", "Interpolation", "interpolation", defaultDrawType = "PROPERTY_ONLY")

        self.newOutput("Falloff", "Falloff", "falloff")

    def draw(self, layout):
        col = layout.column()
        col.prop(self, "soundType", text = "")
        if self.soundType == "AVERAGE":
            col.prop(self, "averageFalloffType", text = "")
        else:
            col.prop(self, "spectrumFalloffType", text = "")

    def getExecutionCode(self):
        yield "if sound is not None and sound.type == self.soundType:"
        if self.useCurrentFrame: yield "    _frame = self.nodeTree.scene.frame_current_final"
        else:                    yield "    _frame = frame"

        if self.soundType == "AVERAGE":
            if self.averageFalloffType == "INDEX_OFFSET":
                yield "    falloff = self.execute_Average_IndexOffset(sound, _frame, offset)"
        elif self.soundType == "SPECTRUM":
            if self.spectrumFalloffType == "INDEX_FREQUENCY":
                yield "    falloff = self.execute_Spectrum_IndexFrequency(sound, _frame, length, interpolation)"

        yield "else: falloff = self.getConstantFalloff(0)"

    def getConstantFalloff(self, value = 0):
        return ConstantFalloff(value)

    def execute_Average_IndexOffset(self, sound, frame, offset):
        return Average_IndexOffset_SoundFalloff(sound, frame, offset)

    def execute_Spectrum_IndexFrequency(self, sound, frame, length, interpolation):
        myList = DoubleList.fromValues(sound.evaluate(frame))
        return DoubleListMixFalloff(myList, length, interpolation)

cdef class Average_IndexOffset_SoundFalloff(BaseFalloff):
    cdef:
        AverageSound sound
        float frame, offsetInverse

    def __cinit__(self, AverageSound sound, float frame, offset):
        self.sound = sound
        self.frame = frame
        self.offsetInverse = 1 / offset if offset != 0 else 0
        self.dataType = "All"
        self.clamped = False

    cdef double evaluate(self, void *object, long index):
        return self.sound.evaluate(self.frame - index * self.offsetInverse)

cdef class DoubleListMixFalloff(BaseFalloff):
    cdef:
        DoubleList myList
        Interpolation interpolation
        long myLength
        long length

    def __cinit__(self, DoubleList myList, length, Interpolation interpolation):
        if len(myList) == 0:
            raise ValueError("list must not be empty")
        self.myList = myList
        self.myLength = len(myList)
        self.length = min(max(length, 1), LONG_MAX)
        self.interpolation = interpolation
        self.dataType = "All"
        self.clamped = False

    cdef double evaluate(self, void *object, long index):
        index = index % self.length
        cdef float pos = <float>index / <float>self.length * <float>self.myLength
        cdef long indexBefore = <int>pos
        cdef float influence = self.interpolation.evaluate(pos - <float>indexBefore)
        cdef long indexAfter
        if indexBefore < self.myLength - 1:
            indexAfter = indexBefore + 1
        else:
            indexAfter = indexBefore
        return self.myList.data[indexBefore] * (1 - influence) + self.myList.data[indexAfter] * influence
