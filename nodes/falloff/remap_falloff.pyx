import bpy
from ... base_types.node import AnimationNode
from ... data_structures cimport Falloff, CompoundFalloff
from ... math cimport Vector3, toVector3, distanceVec3

class RemapFalloffNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_RemapFalloffNode"
    bl_label = "Remap Falloff"

    def create(self):
        self.newInput("Falloff", "Falloff", "inFalloff")
        self.newInput("Float", "New Min", "outputMin", value = 0).setRange(0, 1)
        self.newInput("Float", "New Max", "outputMax", value = 1).setRange(0, 1)
        self.newOutput("Falloff", "Falloff", "outFalloff")

    def execute(self, falloff, outputMin, outputMax):
        return RemapFalloff(falloff, outputMin, outputMax)


cdef class RemapFalloff(CompoundFalloff):
    cdef:
        Falloff falloff
        double outputMin, outputMax
        double factor

    def __cinit__(self, Falloff falloff, double outputMin, double outputMax):
        self.falloff = falloff
        self.outputMin = outputMin
        self.outputMax = outputMax
        self.factor = outputMax - outputMin
        self.clamped = False

    cdef list getDependencies(self):
        return [self.falloff]

    cdef double evaluate(self, double* dependencyResults):
        return dependencyResults[0] * self.factor + self.outputMin
