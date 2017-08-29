import bpy
from ... base_types import AnimationNode
from ... data_structures cimport UnboundedAction, UnboundedActionEvaluator, FloatList, ActionChannel
from ... algorithms.perlin_noise cimport perlinNoise1D

class WiggleLocationActionNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_WiggleLocationActionNode"
    bl_label = "Wiggle Location Action"

    def create(self):
        self.newInput("Float", "Amplitude", "amplitude", value = 1)
        self.newOutput("Action", "Action", "action")

    def execute(self, amplitude):
        channels = ActionChannel.initList([("location", 0, 1, 2)])
        return WiggleAction(amplitude, channels)


cdef class WiggleAction(UnboundedAction):
    cdef float amplitude
    cdef set channels

    def __cinit__(self, float amplitude, list channels):
        self.amplitude = amplitude
        self.channels = set(channels)
        self.checkChannels(channels)

    cdef set getChannelSet(self):
        return self.channels

    cdef UnboundedActionEvaluator getEvaluator_Limited(self, list channels):
        cdef FloatList factors
        factors = FloatList.fromValue(self.amplitude, length = len(channels))
        return WiggleActionEvaluator(factors)

cdef class WiggleActionEvaluator(UnboundedActionEvaluator):
    cdef FloatList factors

    def __cinit__(self, FloatList factors):
        self.factors = factors
        self.channelAmount = len(factors)

    cdef void evaluate(self, float frame, Py_ssize_t index, float *target):
        cdef Py_ssize_t i
        for i in range(self.factors.length):
            target[i] = self.factors.data[i] * perlinNoise1D(frame / 20 + index * 123124 + i * 423543, 0.5, 3)
