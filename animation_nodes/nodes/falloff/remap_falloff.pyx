import bpy
import cython
from ... base_types import AnimationNode
from . constant_falloff import ConstantFalloff
from ... algorithms.interpolations import Linear as LinearInterpolation
from ... data_structures cimport Falloff, CompoundFalloff, Interpolation

class RemapFalloffNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_RemapFalloffNode"
    bl_label = "Remap Falloff"

    def create(self):
        self.newInput("Falloff", "Falloff", "inFalloff")
        self.newInput("Float", "Input Min", "inMin", value = 0)
        self.newInput("Float", "Input Max", "inMax", value = 1)
        self.newInput("Float", "Output Min", "outMin", value = 0)
        self.newInput("Float", "Output Max", "outMax", value = 1)
        self.newInput("Interpolation", "Interpolation", "interpolation",
            defaultDrawType = "PROPERTY_ONLY")

        self.newOutput("Falloff", "Falloff", "outFalloff")

    def execute(self, falloff, inMin, inMax, outMin, outMax, interpolation):
        if inMax == inMin: return ConstantFalloff(0)
        if isinstance(interpolation, LinearInterpolation):
            return RemapFalloff(falloff, inMin, inMax, outMin, outMax)
        else:
            return RemapInterpolatedFalloff(falloff, inMin, inMax, outMin, outMax, interpolation)


cdef class RemapFalloff(CompoundFalloff):
    cdef:
        Falloff falloff
        float inMin, outMin
        float inLength, outLength

    def __cinit__(self, Falloff falloff, float inMin, float inMax, float outMin, float outMax):
        self.falloff = falloff
        self.inMin = inMin
        self.outMin = outMin
        self.inLength = inMax - inMin
        self.outLength = outMax - outMin
        self.clamped = falloff.clamped and 0 <= min(outMin, outMax) <= max(outMin, outMax) <= 1

    cdef list getDependencies(self):
        return [self.falloff]

    @cython.cdivision(True)
    cdef float evaluate(self, float *dependencyResults):
        return self.outMin + ((dependencyResults[0] - self.inMin) / self.inLength) * self.outLength

cdef class RemapInterpolatedFalloff(CompoundFalloff):
    cdef:
        Falloff falloff
        float inMin, outMin
        float inLength, outLength
        Interpolation interpolation

    def __cinit__(self, Falloff falloff, float inMin, float inMax,
            float outMin, float outMax, Interpolation interpolation):
        self.falloff = falloff
        self.inMin = inMin
        self.outMin = outMin
        self.inLength = inMax - inMin
        self.outLength = outMax - outMin
        self.interpolation = interpolation
        self.clamped = falloff.clamped and 0 <= min(outMin, outMax) <= max(outMin, outMax) <= 1

    cdef list getDependencies(self):
        return [self.falloff]

    @cython.cdivision(True)
    cdef float evaluate(self, float *dependencyResults):
        cdef float value = self.interpolation.evaluate((dependencyResults[0] - self.inMin) / self.inLength)
        return self.outMin + value * self.outLength
