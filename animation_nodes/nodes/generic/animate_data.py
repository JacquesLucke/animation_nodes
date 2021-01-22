import bpy
from bpy.props import *
from . mix_data import getMixCode
from ... utils.math import mixEulers
from ... events import executionCodeChanged
from ... base_types import AnimationNode, VectorizedSocket

from . c_utils import (
    mixColorLists,
    mixEulerLists,
    mixDoubleLists,
    mixVectorLists,
    mixQuaternionLists,
    executeTimeList,
    calculateInfluenceList,
)
from ... data_structures import (
    Color,
    Matrix4x4List,
    VirtualColorList,
    VirtualEulerList,
    VirtualDoubleList,
    VirtualVector3DList,
    VirtualMatrix4x4List,
    VirtualQuaternionList,
)

class AnimateDataNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_AnimateDataNode"
    bl_label = "Animate Data"
    bl_width_default = 160
    dynamicLabelType = "ALWAYS"

    onlySearchTags = True
    searchTags = [ ("Animate Matrix", {"dataType" : repr("Matrix")}),
                   ("Animate Vector", {"dataType" : repr("Vector")}),
                   ("Animate Float", {"dataType" : repr("Float")}),
                   ("Animate Color", {"dataType" : repr("Color")}),
                   ("Animate Euler", {"dataType" : repr("Euler")}),
                   ("Animate Quaternion", {"dataType" : repr("Quaternion")}) ]

    dataType: StringProperty(default = "Float", update = AnimationNode.refresh)

    useListA: VectorizedSocket.newProperty()
    useListB: VectorizedSocket.newProperty()
    useListC: VectorizedSocket.newProperty()
    useListD: VectorizedSocket.newProperty()

    def create(self):
        self.newInput(VectorizedSocket("Float", "useListA",
            ("Time", "time"), ("Times", "times")))
        self.newInput(VectorizedSocket(self.dataType, ["useListB"],
            ("Start", "start"), ("Starts", "starts")))
        self.newInput(VectorizedSocket(self.dataType, ["useListC"],
            ("End", "end"), ("Ends", "ends")))
        self.newInput("Interpolation", "interpolation", defaultDrawType = "PROPERTY_ONLY")
        self.newInput(VectorizedSocket("Float", "useListD",
            ("Duration", "duration", dict(value = 20, minValue = 0.001)),
            ("Durations", "durations")))

        self.newOutput(VectorizedSocket("Float", ["useListA", "useListB",
            "useListC", "useListD"], ("Time", "outTime"), ("Times", "outTimes")))
        self.newOutput(VectorizedSocket(self.dataType, ["useListA", "useListB", 
            "useListC", "useListD"], ("Result", "result"), ("Results", "results")))

    def drawLabel(self):
        return "Animate " + self.inputs[1].dataType

    def getExecutionCode(self, required):
        if any([self.useListA, self.useListB, self.useListC, self.useListD]):
            args = ", ".join(socket.identifier for socket in self.inputs)
            yield "results, outTimes = self.executeDataList({})".format(args)

        else:
            yield "finalDuration = max(duration, 0.0001)"
            yield "influence = max(min(time / finalDuration, 1.0), 0.0)"
            yield "influence = interpolation(influence)"
            yield getMixCode(self.dataType, "start", "end", "influence", "result")
            yield "outTime = time - finalDuration"

    def executeDataList(self, time, start, end, interpolation, duration):
        times = VirtualDoubleList.create(time, 0)
        durations = VirtualDoubleList.create(duration, 0)

        if self.dataType == "Float":
            starts, ends = VirtualDoubleList.createMultiple((start, 0), (end, 0))      
            amount = VirtualDoubleList.getMaxRealLength(times, starts, ends, durations)
            factors = calculateInfluenceList(times, interpolation, durations, amount)
            _factors = VirtualDoubleList.create(factors, 0)
            return mixDoubleLists(starts, ends, _factors, amount), executeTimeList(times, durations, amount)
        elif self.dataType == "Vector":
            starts, ends = VirtualVector3DList.createMultiple((start, 0), (end, 0))
            amount = VirtualDoubleList.getMaxRealLength(times, starts, ends, durations)
            factors = calculateInfluenceList(times, interpolation, durations, amount)
            _factors = VirtualDoubleList.create(factors, 0)
            return mixVectorLists(starts, ends, _factors, amount), executeTimeList(times, durations, amount)
        elif self.dataType == "Quaternion":
            starts, ends = VirtualQuaternionList.createMultiple((start, 0), (end, 0))
            amount = VirtualDoubleList.getMaxRealLength(times, starts, ends, durations)
            factors = calculateInfluenceList(times, interpolation, durations, amount)
            _factors = VirtualDoubleList.create(factors, 0)
            return mixQuaternionLists(starts, ends, _factors, amount), executeTimeList(times, durations, amount)
        elif self.dataType == "Matrix":
            starts, ends = VirtualMatrix4x4List.createMultiple((start, 0), (end, 0))
            amount = VirtualDoubleList.getMaxRealLength(times, starts, ends, durations)
            factors = calculateInfluenceList(times, interpolation, durations, amount)
            _factors = VirtualDoubleList.create(factors, 0)
            return mixMatrixLists(starts, ends, _factors, amount), executeTimeList(times, durations, amount)
        elif self.dataType == "Color":
            starts, ends = VirtualColorList.createMultiple((start, 0), (end, 0))
            amount = VirtualDoubleList.getMaxRealLength(times, starts, ends, durations)
            factors = calculateInfluenceList(times, interpolation, durations, amount)
            _factors = VirtualDoubleList.create(factors, 0)
            return mixColorLists(starts, ends, _factors, amount), executeTimeList(times, durations, amount)
        elif self.dataType == "Euler":
            starts, ends = VirtualEulerList.createMultiple((start, 0), (end, 0))
            amount = VirtualDoubleList.getMaxRealLength(times, starts, ends, durations)
            factors = calculateInfluenceList(times, interpolation, durations, amount)
            _factors = VirtualDoubleList.create(factors, 0)
            return mixEulerLists(starts, ends, _factors, amount), executeTimeList(times, durations, amount)

