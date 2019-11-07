# distutils: language = c++
# setup: options = c++11

import bpy
from ... base_types import AnimationNode
from ... libs.FastNoiseSIMD import Noise3DNodeBase

from ... math cimport Vector3
from ... data_structures cimport BaseFalloff
from ... libs.FastNoiseSIMD cimport PyNoise

class NoiseFalloffNode(bpy.types.Node, AnimationNode, Noise3DNodeBase):
    bl_idname = "an_NoiseFalloffNode"
    bl_label = "Noise Falloff"

    def create(self):
        self.createNoiseInputs()
        self.newOutput("Falloff", "Falloff", "falloff")

    def draw(self, layout):
        self.drawNoiseSettings(layout)

    def drawAdvanced(self, layout):
        self.drawAdvancedNoiseSettings(layout)

    def execute(self, *settings):
        cdef PyNoise noise = self.getNoiseObject(settings)
        return NoiseFalloff(noise)

cdef class NoiseFalloff(BaseFalloff):
    cdef PyNoise noise
    def __cinit__(self, PyNoise noise):
        self.noise = noise
        self.clamped = False
        self.dataType = "Location"

    cdef float evaluate(self, void *value, Py_ssize_t index):
        return self.noise.calculateSingle_LowLevel(<Vector3*>value)

    cdef void evaluateList(self, void *values, Py_ssize_t startIndex,
                            Py_ssize_t amount, float *target):
        self.noise.calculateList_LowLevel(<Vector3*>values, amount, target)
