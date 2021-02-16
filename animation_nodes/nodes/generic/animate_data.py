import bpy
from bpy.props import *
from . mix_data import getMixCode
from ... events import executionCodeChanged
from ... base_types import AnimationNode, VectorizedSocket

dataTypeToVirtualListMapping = {
    "Euler" : "VirtualEulerList",
    "Color" : "VirtualColorList",
    "Float" : "VirtualDoubleList",
    "Vector" : "VirtualVector3DList",
    "Matrix" : "VirtualMatrix4x4List",
    "Quaternion" : "VirtualQuaternionList"
}

dataTypeToMixDataListMapping = {
    "Euler" : "mixEulerLists",
    "Color" : "mixColorLists",
    "Float" : "mixDoubleLists",
    "Vector" : "mixVectorLists",
    "Quaternion" : "mixQuaternionLists"
}

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

    useListTime: VectorizedSocket.newProperty()
    useListStartTime: VectorizedSocket.newProperty()
    useListStart: VectorizedSocket.newProperty()
    useListEnd: VectorizedSocket.newProperty()
    useListDuration: VectorizedSocket.newProperty()

    def create(self):
        self.newInput(VectorizedSocket("Float", "useListTime",
            ("Time", "time"), ("Times", "time")))
        self.newInput(VectorizedSocket("Float", "useListStartTime",
            ("Start Time", "startTime", dict(value = 0)), ("Start Times", "startTime")), hide = True)
        self.newInput(VectorizedSocket(self.dataType, "useListStart",
            ("Start Value", "startValue"), ("Start Values", "startValue")))
        self.newInput(VectorizedSocket(self.dataType, "useListEnd",
            ("End Value", "endValue"), ("End Values", "endValue")))
        self.newInput("Interpolation", "interpolation", defaultDrawType = "PROPERTY_ONLY")
        self.newInput(VectorizedSocket("Float", "useListDuration",
            ("Duration", "duration", dict(value = 20, minValue = 0.001)),
            ("Durations", "duration")))

        self.newOutput(VectorizedSocket(self.dataType, ["useListTime", "useListStartTime", "useListStart",
            "useListEnd", "useListDuration"], ("Result", "result"), ("Results", "results")))
        self.newOutput(VectorizedSocket("Float", ["useListTime", "useListStartTime", "useListStart",
            "useListEnd", "useListDuration"], ("Time", "outTime"), ("Times", "outTimes")))

    def drawLabel(self):
        return "Animate " + self.inputs[1].dataType

    def getExecutionCode(self, required):
        if any([self.useListTime, self.useListStartTime, self.useListStart, self.useListEnd, self.useListDuration]):
            yield "times = AN.data_structures.VirtualDoubleList.create(time, 0)"
            yield "startTimes = AN.data_structures.VirtualDoubleList.create(startTime, 0)"
            yield "durations = AN.data_structures.VirtualDoubleList.create(duration, 0)"
            yield f"startValues, endValues = AN.data_structures.{dataTypeToVirtualListMapping[self.dataType]}.createMultiple((startValue, 0), (endValue, 0))"
            yield "amount = AN.data_structures.VirtualDoubleList.getMaxRealLength(times, startTimes, startValues, endValues, durations)"
            yield "factors = AN.nodes.generic.c_utils.calculateInfluenceList(times, startTimes, interpolation, durations, amount)"
            yield "_factors = AN.data_structures.VirtualDoubleList.create(factors, 0)"
            yield "outTimes = AN.nodes.generic.c_utils.executeTimeList(times, startTimes, durations, amount)"

            if self.dataType == "Matrix":
                yield "results = AN.nodes.generic.mix_data.mixMatrixLists(startValues, endValues, _factors, amount)"
            else:
                yield f"results = AN.nodes.generic.c_utils.{dataTypeToMixDataListMapping[self.dataType]}(startValues, endValues, _factors, amount)"

        else:
            yield "finalDuration = max(duration, 0.0001)"
            yield "influence = max(min((time - startTime) / finalDuration, 1.0), 0.0)"
            yield "influence = interpolation(influence)"
            yield getMixCode(self.dataType, "startValue", "endValue", "influence", "result")
            yield "outTime = time - startTime - finalDuration"
