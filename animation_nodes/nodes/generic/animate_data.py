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
    useListStart: VectorizedSocket.newProperty()
    useListEnd: VectorizedSocket.newProperty()
    useListDuration: VectorizedSocket.newProperty()

    def create(self):
        self.newInput(VectorizedSocket("Float", "useListTime",
            ("Time", "time"), ("Times", "time")))
        self.newInput(VectorizedSocket(self.dataType, ["useListStart"],
            ("Start", "start"), ("Starts", "start")))
        self.newInput(VectorizedSocket(self.dataType, ["useListEnd"],
            ("End", "end"), ("Ends", "end")))
        self.newInput("Interpolation", "interpolation", defaultDrawType = "PROPERTY_ONLY")
        self.newInput(VectorizedSocket("Float", "useListDuration",
            ("Duration", "duration", dict(value = 20, minValue = 0.001)),
            ("Durations", "duration")))

        self.newOutput(VectorizedSocket("Float", ["useListTime", "useListStart",
            "useListEnd", "useListDuration"], ("Time", "outTime"), ("Times", "outTimes")))
        self.newOutput(VectorizedSocket(self.dataType, ["useListTime", "useListStart", 
            "useListEnd", "useListDuration"], ("Result", "result"), ("Results", "results")))

    def drawLabel(self):
        return "Animate " + self.inputs[1].dataType

    def getExecutionCode(self, required):
        if any([self.useListTime, self.useListStart, self.useListEnd, self.useListDuration]):
            yield "times = AN.data_structures.VirtualDoubleList.create(time, 0)"
            yield "durations = AN.data_structures.VirtualDoubleList.create(duration, 0)"
            yield f"starts, ends = AN.data_structures.{dataTypeToVirtualListMapping[self.dataType]}.createMultiple((start, 0), (end, 0))"
            yield "amount = AN.data_structures.VirtualDoubleList.getMaxRealLength(times, starts, ends, durations)"
            yield "factors = AN.nodes.generic.c_utils.calculateInfluenceList(times, interpolation, durations, amount)"
            yield "_factors = AN.data_structures.VirtualDoubleList.create(factors, 0)"
            yield "outTimes = AN.nodes.generic.c_utils.executeTimeList(times, durations, amount)"

            if self.dataType == "Matrix":
                yield "results = AN.nodes.generic.mix_data.mixMatrixLists(starts, ends, _factors, amount)"
            else:
                yield f"results = AN.nodes.generic.c_utils.{dataTypeToMixDataListMapping[self.dataType]}(starts, ends, _factors, amount)"

        else:
            yield "finalDuration = max(duration, 0.0001)"
            yield "influence = max(min(time / finalDuration, 1.0), 0.0)"
            yield "influence = interpolation(influence)"
            yield getMixCode(self.dataType, "start", "end", "influence", "result")
            yield "outTime = time - finalDuration"

