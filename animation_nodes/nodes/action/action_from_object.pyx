import bpy
from ... base_types import AnimationNode
from ... utils.attributes import pathBelongsToArray
from ... data_structures cimport (
    BoundedAction, BoundedActionEvaluator,
    PathActionChannel, PathIndexActionChannel
)

class ActionFromObjectNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_ActionFromObjectNode"
    bl_label = "Action from Object"

    def create(self):
        self.newInput("Object", "Object", "object", defaultDrawType = "PROPERTY_ONLY")
        self.newOutput("Action", "Action", "action")

    def execute(self, object):
        cdef list fCurves
        cdef list channels

        try: fCurves = list(object.animation_data.action.fcurves)
        except: return None

        channels = []
        for fCurve in fCurves:
            path, index = fCurve.data_path, fCurve.array_index
            if pathBelongsToArray(object, path):
                channel = PathIndexActionChannel(path, index)
            else:
                channel = PathActionChannel(path)
            channels.append(channel)

        return FCurveAction(fCurves, channels)

cdef class FCurveAction(BoundedAction):
    cdef dict fCurveByChannel
    cdef set channels

    def __cinit__(self, list fCurves, list channels):
        if len(fCurves) != len(channels):
            raise Exception("unequal amount of FCurves and Channels")
        if any(fCurve is None for fCurve in fCurves):
            raise Exception("an FCurve must not be None")

        self.checkChannels(channels)
        self.channels = set(channels)
        self.fCurveByChannel = {c : f for f, c in zip(fCurves, channels)}

    cdef set getChannelSet(self):
        return self.channels

    cdef BoundedActionEvaluator getEvaluator_Limited(self, list channels):
        cdef list fCurves
        fCurves = [self.fCurveByChannel[c] for c in channels]
        return FCurveActionEvaluator(fCurves)

cdef class FCurveActionEvaluator(BoundedActionEvaluator):
    cdef list fCurves
    cdef float start, end, length

    def __cinit__(self, list fCurves):
        self.fCurves = fCurves
        self.channelAmount = len(fCurves)
        self.start, self.end = self.calculateRange(fCurves)
        self.length = self.end - self.start

    cdef calculateRange(self, list fCurves):
        if len(fCurves) == 0:
            return 0, 0

        cdef float start, end
        cdef float _start, _end
        start, end = fCurves[0].range()
        for fCurve in fCurves:
            _start, _end = fCurve.range()
            if _start < start:
                start = _start
            if _end > end:
                end = _end

        if end < start:
            # can happen due to a Blender bug when the user moves a keyframe
            start, end = end, start
            
        return start, end

    cdef void evaluate(self, float frame, Py_ssize_t index, float *target):
        cdef Py_ssize_t i
        for i in range(self.channelAmount):
            target[i] = self.fCurves[i].evaluate(frame)

    cpdef float getStart(self, Py_ssize_t index):
        return self.start

    cpdef float getEnd(self, Py_ssize_t index):
        return self.end

    cpdef float getLength(self, Py_ssize_t index):
        return self.length
