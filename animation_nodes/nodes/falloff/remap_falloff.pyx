import bpy
import cython
from ... base_types import AnimationNode
from ... math cimport Vector3, setVector3, distanceVec3
from ... data_structures cimport Falloff, CompoundFalloff

class RemapFalloffNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_RemapFalloffNode"
    bl_label = "Remap Falloff"

    def create(self):
        self.newInput("Falloff", "Falloff", "inFalloff")
        self.newInput("Float", "Input Min", "inMin", value = 0)
        self.newInput("Float", "Input Max", "inMax", value = 1)
        self.newInput("Float", "Output Min", "outMin", value = 0)
        self.newInput("Float", "Output Max", "outMax", value = 1)

        self.newOutput("Falloff", "Falloff", "outFalloff")

    def execute(self, falloff, inMin, inMax, outMin, outMax):
        return RemapFalloff(falloff, inMin, inMax, outMin, outMax)


cdef class RemapFalloff(CompoundFalloff):
    cdef:
        Falloff falloff
        float inMin, inMax
        float outMin, outMax

    def __cinit__(self, Falloff falloff, float inMin, float inMax, float outMin, float outMax):
        self.falloff = falloff
        self.inMin = inMin
        self.inMax = inMax
        self.outMin = outMin
        self.outMax = outMax
        self.clamped = falloff.clamped and 0 <= min(outMin, outMax) <= max(outMin, outMax) <= 1

    cdef list getDependencies(self):
        return [self.falloff]

    @cython.cdivision(True)
    cdef float evaluate(self, float *dependencyResults):
        if self.inMax == self.inMin: return 0
        return self.outMin + (dependencyResults[0] - self.inMin) / (self.inMax - self.inMin) * (self.outMax - self.outMin)
