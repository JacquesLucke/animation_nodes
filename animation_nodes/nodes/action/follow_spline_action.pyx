import bpy
from ... base_types import AnimationNode
from ... data_structures cimport Spline, BoundedAction, BoundedActionEvaluator, PathIndexActionChannel
from ... math cimport Vector3

class FollowSplineActionNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_FollowSplineActionNode"
    bl_label = "Follow Spline Action"

    def create(self):
        self.newInput("Spline", "Spline", "spline", defaultDrawType = "PROPERTY_ONLY")
        self.newInput("Float", "Duration", "duration", value = 100)
        self.newOutput("Action", "Action", "action")

    def execute(self, spline, duration):
        if not spline.isEvaluable():
            return None

        return FollowSplineAction(spline, duration)


cdef class FollowSplineAction(BoundedAction):
    cdef Spline spline
    cdef float duration

    def __cinit__(self, Spline spline, float duration):
        self.spline = spline
        self.duration = max(duration, 0.001)
        self.channels = set(PathIndexActionChannel.initList([("location", 0, 1, 2)]))

    cdef BoundedActionEvaluator getEvaluator_Limited(self, list channels):
        return FollowSplineActionEvaluator(self.spline, self.duration)

cdef class FollowSplineActionEvaluator(BoundedActionEvaluator):
    cdef Spline spline
    cdef float duration

    def __cinit__(self, Spline spline, float duration):
        self.spline = spline
        self.duration = duration
        self.channelAmount = 3

    cdef void evaluate(self, float frame, Py_ssize_t index, float *target):
        cdef float t = min(max(frame / self.duration, 0), 1)
        self.spline.evaluate_LowLevel(t, <Vector3*>target)
