import bpy
from bpy.props import *
from ... events import propertyChanged
from ... base_types import AnimationNode
from ... graphics import Rectangle
from ... graphics.drawing_2d import drawVerticalLine
from ... data_structures cimport (
    BoundedAction, BoundedActionEvaluator,
    FloatList, BooleanList
)

class ChainActionsNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_ChainActionsNode"
    bl_label = "Chain Actions"
    errorHandlingType = "EXCEPTION"

    relative = BoolProperty(name = "Relative", default = True,
        description = "Use last frame of first action as starting point of the second.",
        update = propertyChanged)

    def create(self):
        self.newInput("Action", "A", "a")
        self.newInput("Action", "B", "b")
        self.newOutput("Action", "Chained Action")

    def draw(self, layout):
        layout.prop(self, "relative")

    def execute(self, a, b):
        if a is None:
            return b
        if b is None:
            return a
        if isinstance(a, BoundedAction) and isinstance(b, BoundedAction):
            return ChainAction(a, b, self.relative)
        else:
            self.raiseErrorMessage("only bounded actions can be chained")

cdef class ChainAction(BoundedAction):
    cdef BoundedAction a, b
    cdef bint relative
    cdef set channels

    def __cinit__(self, BoundedAction a, BoundedAction b, bint relative):
        self.a = a
        self.b = b
        self.relative = relative
        self.channels = a.getChannelSet() | b.getChannelSet()

    cdef set getChannelSet(self):
        return self.channels

    cdef BoundedActionEvaluator getEvaluator_Limited(self, list channels):
        # TODO: generalize decision which elements to add/multiply
        multiplyElements = BooleanList.fromValues(["scale" in c.path for c in channels])
        return ChainActionEvaluator(
            self.a.getEvaluator(channels),
            self.b.getEvaluator(channels),
            self.relative,
            multiplyElements
        )

cdef class ChainActionEvaluator(BoundedActionEvaluator):
    cdef BoundedActionEvaluator a, b
    cdef bint relative
    cdef FloatList relativeBuffer
    cdef BooleanList multiplyElements

    def __cinit__(self, BoundedActionEvaluator a, BoundedActionEvaluator b,
                  bint relative, BooleanList multiplyElements):
        self.a = a
        self.b = b
        self.relative = relative
        self.multiplyElements = multiplyElements
        self.relativeBuffer = FloatList(length = a.channelAmount)
        self.channelAmount = a.channelAmount

    cdef void evaluate(self, float frame, Py_ssize_t index, float *target):
        cdef float aEnd = self.a.getEnd(index)
        cdef Py_ssize_t i
        if frame < aEnd:
            self.a.evaluate(frame, index, target)
        else:
            if self.relative:
                self.a.evaluate(min(frame, aEnd), index, self.relativeBuffer.data)
                self.b.evaluate(frame - aEnd + self.b.getStart(index), index, target)
                for i in range(self.channelAmount):
                    if self.multiplyElements.data[i]:
                        target[i] *= self.relativeBuffer.data[i]
                    else:
                        target[i] += self.relativeBuffer.data[i]
            else:
                self.b.evaluate(frame - aEnd + self.b.getStart(index), index, target)

    cpdef float getStart(self, Py_ssize_t index):
        return self.a.getStart(index)

    cpdef float getEnd(self, Py_ssize_t index):
        return self.a.getEnd(index) + self.b.getLength(index)

    cpdef float getLength(self, Py_ssize_t index):
        return self.a.getLength(index) + self.b.getLength(index)

    def drawPreview(self, Py_ssize_t index, rectangle):
        aEnd = self.a.getEnd(index)
        recA = rectangle.getClampedSubFrameRange(self.a.getStart(index), aEnd)
        recB = rectangle.getClampedSubFrameRange(aEnd, aEnd + self.b.getLength(index))
        recB.shiftFrameRange(self.b.getStart(index) - aEnd)
        if recA.width > 0:
            self.a.drawPreview(index, recA)
        if recB.width > 0:
            self.b.drawPreview(index, recB)
        if recA.width > 0 and recB.width > 0:
            drawVerticalLine(recA.right, rectangle.top, -rectangle.height,
                thickness = 1, color = (0.1, 0.1, 0.1, 1))
