import bpy
from ... base_types import AnimationNode
from ... data_structures cimport BoundedAction, BoundedActionEvaluator

class DelayActionNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_DelayActionNode"
    bl_label = "Delay Action"

    def create(self):
        self.newInput("Action", "Action", "inAction")
        self.newInput("Float", "Delay", "delay", value = 5)
        self.newOutput("Action", "Action", "outAction")

    def execute(self, action, delay):
        if action is None:
            return None

        return DelayBoundedAction(action, delay)


cdef class DelayBoundedAction(BoundedAction):
    cdef BoundedAction action
    cdef float delay

    def __cinit__(self, BoundedAction action, float delay):
        self.action = action
        self.delay = delay
        self.channels = action.channels

    cdef BoundedActionEvaluator getEvaluator_Limited(self, list channels):
        return DelayBoundedActionEvaluator(self.action.getEvaluator_Limited(channels), self.delay)

cdef class DelayBoundedActionEvaluator(BoundedActionEvaluator):
    cdef BoundedActionEvaluator evaluator
    cdef float delay

    def __cinit__(self, BoundedActionEvaluator evaluator, float delay):
        self.evaluator = evaluator
        self.delay = delay
        self.channelAmount = evaluator.channelAmount

    cdef void evaluate(self, float frame, Py_ssize_t index, float *target):
        self.evaluator.evaluate(frame - index * self.delay, index, target)

    cpdef float getStart(self, Py_ssize_t index):
        return self.evaluator.getStart(index) + index * self.delay

    cpdef float getEnd(self, Py_ssize_t index):
        return self.evaluator.getEnd(index) + index * self.delay

    cpdef float getLength(self, Py_ssize_t index):
        return self.evaluator.getLength(index)
