import bpy
from . spline_evaluation_base import SplineEvaluationBase
from ... base_types import AnimationNode, VectorizedSocket
from ... data_structures import VirtualDoubleList, DoubleList

class GetSplineLengthNode(bpy.types.Node, AnimationNode, SplineEvaluationBase):
    bl_idname = "an_GetSplineLengthNode"
    bl_label = "Get Spline Length"

    useSplineList: VectorizedSocket.newProperty()
    useStartList: VectorizedSocket.newProperty()
    useEndList: VectorizedSocket.newProperty()

    def create(self):
        socket = self.newInput(VectorizedSocket("Spline", "useSplineList",
            ("Spline", "spline"), ("Splines", "splines")))
        socket.defaultDrawType = "PROPERTY_ONLY"
        socket.dataIsModified = True

        self.newInput(VectorizedSocket("Float", "useStartList",
            ("Start", "start"),
            ("Starts", "starts")))
        self.newInput(VectorizedSocket("Float", "useEndList",
            ("End", "end"),
            ("Ends", "ends")))

        self.newOutput(VectorizedSocket("Float", ["useSplineList", "useStartList", "useEndList"],
            ("Length", "length"),
            ("Lengths", "lengths")))

    def draw(self, layout):
        layout.prop(self, "parameterType", text = "")

    def drawAdvanced(self, layout):
        col = layout.column()
        col.active = self.parameterType == "UNIFORM"
        col.prop(self, "resolution")

    def getExecutionFunctionName(self):
        if self.useSplineList:
            if self.useStartList and self.useEndList:
                return "execute_MultipleSplines_MultipleStarts_MultipleEnds"
            elif self.useStartList:
                return "execute_MultipleSplines_MultipleStarts"
            elif self.useEndList:
                return "execute_MultipleSplines_MultipleEnds"
            else:
                return "execute_MultipleSplines_SingleStart_SingleEnd"
        else:
            if self.useStartList and self.useEndList:
                return "execute_SingleSpline_MultipleStarts_MultipleEnds"
            elif self.useStartList:
                return "execute_SingleSpline_MultipleStarts"
            elif self.useEndList:
                return "execute_SingleSpline_MultipleEnds"
            else:
                return "execute_SingleSpline_SingleStart_SingleEnd"

    def execute_MultipleSplines_MultipleStarts_MultipleEnds(self, splines, starts, ends):
        amount = len(splines)
        starts = VirtualDoubleList.create(starts, 0)
        ends = VirtualDoubleList.create(ends, 0)
        lengths = DoubleList(amount, 0)
        for i, spline in enumerate(splines):
            lengths[i] = self.execute_SingleSpline_SingleStart_SingleEnd(spline, starts[i], ends[i])
        return lengths

    def execute_MultipleSplines_MultipleStarts(self, splines, starts, end):
        amount = len(splines)
        starts = VirtualDoubleList.create(starts, 0)
        lengths = DoubleList(amount, 0)
        for i, spline in enumerate(splines):
            lengths[i] = self.execute_SingleSpline_SingleStart_SingleEnd(spline, starts[i], end)
        return lengths

    def execute_MultipleSplines_MultipleEnds(self, splines, start, ends):
        amount = len(splines)
        ends = VirtualDoubleList.create(ends, 0)
        lengths = DoubleList(amount, 0)
        for i, spline in enumerate(splines):
            lengths[i] = self.execute_SingleSpline_SingleStart_SingleEnd(spline, start, ends[i])
        return lengths

    def execute_MultipleSplines_SingleStart_SingleEnd(self, splines, start, end):
        amount = len(splines)
        lengths = DoubleList(amount, 0)
        for i, spline in enumerate(splines):
            lengths[i] = self.execute_SingleSpline_SingleStart_SingleEnd(spline, start, end)
        return lengths


    def execute_SingleSpline_MultipleStarts_MultipleEnds(self, spline, starts, ends):
        amount = max(len(starts), len(ends))
        starts = VirtualDoubleList.create(starts, 0)
        ends = VirtualDoubleList.create(ends, 0)
        lengths = DoubleList(amount, 0)
        for i in range(amount):
            lengths[i] = self.execute_SingleSpline_SingleStart_SingleEnd(spline, starts[i], ends[i])
        return lengths

    def execute_SingleSpline_MultipleStarts(self, spline, starts, end):
        amount = len(starts)
        lengths = DoubleList(amount, 0)
        for i in range(amount):
            lengths[i] = self.execute_SingleSpline_SingleStart_SingleEnd(spline, starts[i], end)
        return lengths

    def execute_SingleSpline_MultipleEnds(self, spline, start, ends):
        amount = len(ends)
        lengths = DoubleList(amount, 0)
        for i in range(amount):
            lengths[i] = self.execute_SingleSpline_SingleStart_SingleEnd(spline, start, ends[i])
        return lengths

    def execute_SingleSpline_SingleStart_SingleEnd(self, spline, start, end):
        if spline.isEvaluable():
            start = min(max(start, 0), 1)
            end = min(max(end, 0), 1)

            if start == 0 and end == 1:
                # to get a more exact result on polysplines currently
                return spline.getLength(self.resolution)

            if self.parameterType == "UNIFORM":
                spline.ensureUniformConverter(self.resolution)
                start = spline.toUniformParameter(start)
                end = spline.toUniformParameter(end)
            return spline.getPartialLength(start, end, self.resolution)
        return 0.0
