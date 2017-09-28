import bpy
from ... base_types import AnimationNode
from ... graphics import Rectangle
from ... graphics.drawing_2d import drawHorizontalLine
from ... data_structures cimport (
    FloatList,
    Action, ActionEvaluator,
    BoundedAction, BoundedActionEvaluator,
    UnboundedAction, UnboundedActionEvaluator
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
            return overlay
        if overlay is None:
            return base
        if isinstance(base, BoundedAction):
            return BoundedOverlayAction(base, overlay)
        elif isinstance(base, UnboundedAction):
            return UnboundedOverlayAction(base, overlay)


cdef class BoundedOverlayAction(BoundedAction):
    cdef BoundedAction base
    cdef Action overlay
    cdef set channels

    def __cinit__(self, BoundedAction base, Action overlay):
        self.base = base
        self.overlay = overlay
        self.channels = base.getChannelSet() | overlay.getChannelSet()

    cdef set getChannelSet(self):
        return self.channels

    cdef BoundedActionEvaluator getEvaluator_Limited(self, list channels):
        base = self.base.getEvaluator(channels)
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

    def drawPreview(self, Py_ssize_t index, rectangle):
        sub = rectangle.getClampedSubFrameRange(self.getStart(index), self.getEnd(index))
        overlayRec = type(sub)(sub.left, sub.top,
                               sub.right, sub.centerY,
                               sub.startFrame, sub.endFrame)
        baseRec = type(sub)(sub.left, sub.centerY,
                            sub.right, sub.bottom,
                            sub.startFrame, sub.endFrame)
        if overlayRec.width > 0:
            self.overlay.drawPreview(index, overlayRec)
        if overlayRec.width > 0:
            self.base.drawPreview(index, baseRec)
        if sub.width > 0:
            drawHorizontalLine(sub.left, sub.centerY, sub.width,
                color = (0.1, 0.1, 0.1, 1.0), thickness = 1)


cdef class UnboundedOverlayAction(UnboundedAction):
    cdef UnboundedAction base
    cdef Action overlay
    cdef set channels

    def __cinit__(self, UnboundedAction base, Action overlay):
        self.base = base
        self.overlay = overlay
        self.channels = base.getChannelSet() | overlay.getChannelSet()

    cdef set getChannelSet(self):
        return self.channels

    cdef UnboundedActionEvaluator getEvaluator_Limited(self, list channels):
        base = self.base.getEvaluator(channels)
        overlay = self.overlay.getEvaluator(channels)
        return UnboundedOverlayActionEvaluator(base, overlay)

cdef class UnboundedOverlayActionEvaluator(UnboundedActionEvaluator):
    cdef UnboundedActionEvaluator base
    cdef ActionEvaluator overlay
    cdef FloatList overlayTarget

    def __cinit__(self, UnboundedActionEvaluator base, ActionEvaluator overlay):
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
