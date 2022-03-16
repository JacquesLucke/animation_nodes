import bpy
from . spline_evaluation_base import SplineEvaluationBase
from ... base_types import AnimationNode, VectorizedSocket
from ... data_structures import VirtualDoubleList, VirtualPyList, DoubleList, PolySpline

class GetSplineLengthNode(bpy.types.Node, AnimationNode, SplineEvaluationBase):
    bl_idname = "an_GetSplineLengthNode"
    bl_label = "Get Spline Length"

    useSplineList: VectorizedSocket.newProperty()
    useStartList: VectorizedSocket.newProperty()
    useEndList: VectorizedSocket.newProperty()

    def create(self):
        socket = self.newInput(VectorizedSocket("Spline", "useSplineList",
            ("Spline", "spline"), ("Splines", "spline")))
        socket.defaultDrawType = "PROPERTY_ONLY"

        self.newInput(VectorizedSocket("Float", "useStartList",
            ("Start", "start"),
            ("Starts", "start")))
        self.newInput(VectorizedSocket("Float", "useEndList",
            ("End", "end"),
            ("Ends", "end")))

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
        if any([self.useSplineList, self.useStartList, self.useEndList]):
            return "execute_MultipleSplines_MultipleStarts_MultipleEnds"
        else:
            return "execute_SingleSpline_SingleStart_SingleEnd"

    def execute_MultipleSplines_MultipleStarts_MultipleEnds(self, spline, start, end):
        splines = VirtualPyList.create(spline, PolySpline())
        starts, ends = VirtualDoubleList.createMultiple((start, 0), (end, 0))
        amount = VirtualDoubleList.getMaxRealLength(splines, starts, ends)

        lengths = DoubleList(amount, 0)
        for i in range(amount):
            lengths[i] = self.execute_SingleSpline_SingleStart_SingleEnd(splines[i], starts[i], ends[i])
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
