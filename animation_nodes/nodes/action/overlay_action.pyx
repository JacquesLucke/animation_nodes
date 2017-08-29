import bpy
from ... base_types import AnimationNode
from ... data_structures cimport (
    FloatList,
    Action, ActionEvaluator,
    BoundedAction, BoundedActionEvaluator
)

class OverlayActionNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_OverlayActionNode"
    bl_label = "Overlay Action"

    def create(self):
        self.newInput("Action", "Base", "base")
        self.newInput("Action", "Overlay", "overlay")
        self.newOutput("Action", "Action", "action")

    def execute(self, base, overlay):
        if base is None:
            return None
        if overlay is None:
            return base
        return OverlayAction(base, overlay)


cdef class OverlayAction(BoundedAction):
    cdef BoundedAction base
    cdef Action overlay

    def __cinit__(self, BoundedAction base, Action overlay):
        self.base = base
        self.overlay = overlay

    cdef set getChannelSet(self):
        return self.base.getChannelSet()

    cdef BoundedActionEvaluator getEvaluator_Limited(self, list channels):
        base = self.base.getEvaluator_Limited(channels)
        overlay = self.overlay.getEvaluator(channels)
        return OverlayActionEvaluator(base, overlay)

cdef class OverlayActionEvaluator(BoundedActionEvaluator):
    cdef BoundedActionEvaluator base
    cdef ActionEvaluator overlay
    cdef FloatList overlayTarget

    def __cinit__(self, BoundedActionEvaluator base, ActionEvaluator overlay):
        self.base = base
        self.overlay = overlay
        self.overlayTarget = FloatList(length = overlay.channelAmount)
        self.channelAmount = base.channelAmount

    cdef void evaluate(self, float frame, Py_ssize_t index, float *target):
        self.base.evaluate(frame, index, target)
        self.overlay.evaluate(frame, index, self.overlayTarget.data)

        cdef Py_ssize_t i
        for i in range(self.channelAmount):
            target[i] += self.overlayTarget.data[i]

    cpdef float getStart(self, Py_ssize_t index):
        return self.base.getStart(index)

    cpdef float getEnd(self, Py_ssize_t index):
        return self.base.getEnd(index)

    cpdef float getLength(self, Py_ssize_t index):
        return self.base.getLength(index)
