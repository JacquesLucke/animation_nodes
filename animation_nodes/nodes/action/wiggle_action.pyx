import bpy
from bpy.props import *
from ... base_types import AnimationNode
from ... algorithms.perlin_noise cimport perlinNoise1D
from ... data_structures cimport (
    UnboundedAction,
    UnboundedActionEvaluator,
    FloatList,
    PathIndexActionChannel
)

class WiggleActionNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_WiggleActionNode"
    bl_label = "Wiggle Action"

    channelName = StringProperty()
    channelIndex = IntProperty()

    def create(self):
        self.newInput("Integer", "Seed", "seed")
        self.newInput("Float", "Amplitude", "amplitude", value = 1)
        self.newOutput("Action", "Action", "action")

    def draw(self, layout):
        layout.prop(self, "channelName", text = "")
        layout.prop(self, "channelIndex", text = "")

    def execute(self, seed, amplitude):
        channels = [PathIndexActionChannel(self.channelName, self.channelIndex)]
        return WiggleAction(amplitude, channels, seed)

cdef class WiggleAction(UnboundedAction):
    cdef float amplitude
    cdef set channels
    cdef Py_ssize_t seed

    def __cinit__(self, float amplitude, list channels, Py_ssize_t seed):
        self.amplitude = amplitude
        self.seed = seed
        self.channels = set(channels)
        self.checkChannels(channels)

    cdef set getChannelSet(self):
        return self.channels

    cdef UnboundedActionEvaluator getEvaluator_Limited(self, list channels):
        cdef FloatList factors
        factors = FloatList.fromValue(self.amplitude, length = len(channels))
        return WiggleActionEvaluator(factors, self.seed)

cdef class WiggleActionEvaluator(UnboundedActionEvaluator):
    cdef FloatList factors
    cdef Py_ssize_t seed

    def __cinit__(self, FloatList factors, Py_ssize_t seed):
        self.factors = factors
        self.seed = seed
        self.channelAmount = len(factors)

    cdef void evaluate(self, float frame, Py_ssize_t index, float *target):
        cdef Py_ssize_t i
        for i in range(self.factors.length):
            target[i] = self.factors.data[i] * perlinNoise1D(frame / 20 + index * 123124 + i * 43543 + self.seed * 3452, 0.5, 3)
