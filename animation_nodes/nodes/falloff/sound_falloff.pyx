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

indexFrequencyExtensionTypeItems = [
    ("LOOP", "Loop", "", "NONE", 0),
    ("MIRROR", "Mirror", "", "NONE", 1),
    ("EXTEND_LAST", "Extend Last", "NONE", 2),
    ("EXTEND_ZERO", "Extend Zero", "NONE", 3)
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

    indexFrequencyExtensionType = EnumProperty(name = "Index Frequency Extension Type", default = "LOOP",
        items = indexFrequencyExtensionTypeItems, update = AnimationNode.refresh)

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
                self.newInput("Float", "Length", "length", value = 10, minValue = 1)
                self.newInput("Float", "Offset", "offset")
                self.newInput("Interpolation", "Interpolation", "interpolation",
                    defaultDrawType = "PROPERTY_ONLY", category = "QUADRATIC",
                    easeIn = True, easeOut = True)

        self.newOutput("Falloff", "Falloff", "falloff")

    def draw(self, layout):
        col = layout.column()
        col.prop(self, "soundType", text = "")
        if self.soundType == "AVERAGE":
            col.prop(self, "averageFalloffType", text = "")
        else:
            col.prop(self, "spectrumFalloffType", text = "")
            if self.spectrumFalloffType == "INDEX_FREQUENCY":
                col.prop(self, "indexFrequencyExtensionType", text = "")

    def getExecutionCode(self):
        yield "if sound is not None and sound.type == self.soundType:"
        if self.useCurrentFrame: yield "    _frame = self.nodeTree.scene.frame_current_final"
        else:                    yield "    _frame = frame"

        if self.soundType == "AVERAGE":
            if self.averageFalloffType == "INDEX_OFFSET":
                yield "    falloff = self.execute_Average_IndexOffset(sound, _frame, offset)"
        elif self.soundType == "SPECTRUM":
            if self.spectrumFalloffType == "INDEX_FREQUENCY":
                yield "    falloff = self.execute_Spectrum_IndexFrequency(sound, _frame, length, offset, interpolation)"

        yield "else: falloff = self.getConstantFalloff(0)"

    def getConstantFalloff(self, value = 0):
        return ConstantFalloff(value)

    def execute_Average_IndexOffset(self, sound, frame, offset):
        return Average_IndexOffset_SoundFalloff(sound, frame, offset)

    def execute_Spectrum_IndexFrequency(self, sound, frame, length, offset, interpolation):
        type = self.indexFrequencyExtensionType
        myList = DoubleList.fromValues(sound.evaluate(frame))
        return InterpolateDoubleListFalloff.construct(type, myList, length, offset, interpolation)

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

cdef class InterpolateDoubleListFalloff(BaseFalloff):
    cdef:
        DoubleList myList
        Interpolation interpolation
        double length, offset

    @classmethod
    def construct(cls, extensionMode, DoubleList myList, length, offset, interpolation):
        if len(myList) == 0:
            return ConstantFalloff(0)
        if len(myList) == 1 or length == 0:
            return ConstantFalloff(myList[0])

        if extensionMode == "LOOP":
            return Loop_InterpolateDoubleListFalloff(myList, length, offset, interpolation)
        elif extensionMode == "MIRROR":
            return Loop_InterpolateDoubleListFalloff(myList + myList.reversed(), length * 2, offset * 2, interpolation)
        elif extensionMode == "EXTEND_LAST":
            return Extend_InterpolateDoubleListFalloff(myList, length, offset, interpolation)
        elif extensionMode == "EXTEND_ZERO":
            return Extend_InterpolateDoubleListFalloff([0] + myList + [0], length + 2, offset + 1, interpolation)

    # should only be called from subclasses
    def __cinit__(self, DoubleList myList, double length, double offset, Interpolation interpolation):
        self.myList = myList
        self.length = length
        self.offset = offset
        self.interpolation = interpolation
        self.dataType = "All"
        self.clamped = False

    cdef evaluatePosition(self, double x):
        cdef long indexBefore = <int>x
        cdef float influence = self.interpolation.evaluate(x - <float>indexBefore)
        cdef long indexAfter
        if indexBefore < self.myList.length - 1:
            indexAfter = indexBefore + 1
        else:
            indexAfter = indexBefore
        return self.myList.data[indexBefore] * (1 - influence) + self.myList.data[indexAfter] * influence

cdef class Loop_InterpolateDoubleListFalloff(InterpolateDoubleListFalloff):
    cdef double evaluate(self, void *object, long _index):
        cdef double index = (<double>_index + self.offset) % self.length
        cdef double x = index / self.length * self.myList.length
        return self.evaluatePosition(x)

cdef class Extend_InterpolateDoubleListFalloff(InterpolateDoubleListFalloff):
    cdef double evaluate(self, void *object, long _index):
        cdef double index = <double>_index + self.offset
        index = min(max(index, 0), self.length - 1)
        cdef double x = index / self.length * self.myList.length
        return self.evaluatePosition(x)
