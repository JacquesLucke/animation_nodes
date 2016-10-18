import bpy
from ... base_types import AnimationNode
from ... data_structures cimport BaseFalloff

class DelayFalloffNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_DelayFalloffNode"
    bl_label = "Delay Falloff"

    def create(self):
        self.newInput("Float", "Frame", "frame")
        self.newInput("Float", "Duration", "duration", value = 20)
        self.newInput("Float", "Delay", "delay", value = 5)
        self.newOutput("Falloff", "Falloff", "falloff")

    def execute(self, frame, duration, delay):
        return DelayFalloff(frame, duration, delay)


cdef class DelayFalloff(BaseFalloff):
    cdef double frame
    cdef double duration
    cdef double delay

    def __cinit__(self, double frame, double duration, double delay):
        self.frame = frame
        self.duration = duration
        self.delay = delay
        self.clamped = True
        self.dataType = "All"

    cdef double evaluate(self, void* object, long index):
        cdef double localFrame = self.frame - index * self.delay
        if localFrame <= 0: return 0
        if localFrame <= self.duration: return localFrame / self.duration
        return 1
