import bpy
from bpy.props import *
from . mix_data import getMixCode
from ... events import executionCodeChanged
from ... base_types import AnimationNode, VectorizedSocket

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
            yield f"time, start, end, interpolation, duration = {args}"
            yield "times = AN.data_structures.VirtualDoubleList.create(time, 0)"
            yield "durations = AN.data_structures.VirtualDoubleList.create(duration, 0)"
            if self.dataType == "Float":
                yield f"starts, ends = AN.data_structures.VirtualDoubleList.createMultiple((start, 0), (end, 0))"
            elif self.dataType == "Vector":
                yield f"starts, ends = AN.data_structures.VirtualVector3DList.createMultiple((start, 0), (end, 0))"
            elif self.dataType == "Matrix":
                yield f"starts, ends = AN.data_structures.VirtualMatrix4x4List.createMultiple((start, 0), (end, 0))"
            else:
                yield f"starts, ends = AN.data_structures.Virtual{self.dataType}List.createMultiple((start, 0), (end, 0))"
            yield "amount = AN.data_structures.VirtualDoubleList.getMaxRealLength(times, starts, ends, durations)"
            yield "factors = AN.nodes.generic.c_utils.calculateInfluenceList(times, interpolation, durations, amount)"
            yield "_factors = AN.data_structures.VirtualDoubleList.create(factors, 0)"
            yield "outTimes = AN.nodes.generic.c_utils.executeTimeList(times, durations, amount)"
            if self.dataType == "Float":
                yield "results = AN.nodes.generic.c_utils.mixDoubleLists(starts, ends, _factors, amount)"
            elif self.dataType == "Matrix":
                yield "results = AN.nodes.generic.mix_data.mixMatrixLists(starts, ends, _factors, amount)"
            else:
                yield f"results = AN.nodes.generic.c_utils.mix{self.dataType}Lists(starts, ends, _factors, amount)"

        else:
            yield "finalDuration = max(duration, 0.0001)"
            yield "influence = max(min(time / finalDuration, 1.0), 0.0)"
            yield "influence = interpolation(influence)"
            yield getMixCode(self.dataType, "start", "end", "influence", "result")
            yield "outTime = time - finalDuration"

