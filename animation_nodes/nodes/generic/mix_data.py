import bpy
from bpy.props import *
from ... utils.math import mixEulers
from ... events import executionCodeChanged
from ... base_types import AnimationNode, VectorizedSocket
from . c_utils import (
    mixColorLists,
    mixEulerLists,
    mixDoubleLists,
    mixVectorLists,
    mixMatrixLists,
    mixQuaternionLists
)
from ... data_structures import (
    Color,
    VirtualColorList,
    VirtualEulerList,
    VirtualDoubleList,
    VirtualVector3DList,
    VirtualMatrix4x4List,
    VirtualQuaternionList
)

nodeTypes = {
    "Matrix" : "Mix Matrices",
    "Vector" : "Mix Vectors",
    "Float" : "Mix Floats",
    "Color" : "Mix Colors",
    "Euler" : "Mix Eulers",
    "Quaternion" : "Mix Quaternions" }

class MixDataNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_MixDataNode"
    bl_label = "Mix"
    dynamicLabelType = "ALWAYS"

    onlySearchTags = True
    searchTags = [(tag, {"dataType" : repr(type)}) for type, tag in nodeTypes.items()]

    dataType: StringProperty(default = "Float", update = AnimationNode.refresh)

    clampFactor: BoolProperty(name = "Clamp Factor",
        description = "Clamp factor between 0 and 1",
        default = False, update = executionCodeChanged)

    useFactorList: VectorizedSocket.newProperty()
    useAList: VectorizedSocket.newProperty()
    useBList: VectorizedSocket.newProperty()

    def create(self):
        self.newInput(VectorizedSocket("Float", "useFactorList", ("Factor", "factor"),
            ("Factors", "factor")))
        self.newInput(VectorizedSocket(self.dataType, ["useAList"], ("A", "a"), ("As", "a")))
        self.newInput(VectorizedSocket(self.dataType, ["useBList"], ("B", "b"), ("Bs", "b")))

        self.newOutput(VectorizedSocket(self.dataType, ["useAList", "useBList", "useFactorList"],
            ("Result", "result"), ("Results", "results")))

    def draw(self, layout):
        layout.prop(self, "clampFactor")

    def drawLabel(self):
        if any([self.useAList, self.useBList, self.useFactorList]):
            return nodeTypes[self.outputs[0].dataType.strip("List").rstrip()]
        return nodeTypes[self.outputs[0].dataType]

    def getExecutionFunctionName(self):
        if any([self.useAList, self.useBList, self.useFactorList]):
            return "execute_MixDataList"
        else:
            return "execute_MixData"

    def execute_MixData(self, factor, a, b):
        f = factor
        if self.clampFactor:
            f = min(max(factor, 0.0), 1.0)
        return getMixCode(self.dataType, a, b, f)

    def execute_MixDataList(self, factor, mix1, mix2):
        if self.clampFactor:
            if self.useFactorList:
                factor.clamp(0, 1)
            else:
                factor = min(max(factor, 0.0), 1.0)

        factors = VirtualDoubleList.create(factor, 0)

        if self.dataType == "Float":
            mix1s, mix2s = VirtualDoubleList.createMultiple((mix1, 0), (mix2, 0))
            amount = VirtualDoubleList.getMaxRealLength(mix1s, mix2s, factors)
            return mixDoubleLists(mix1s, mix2s, factors, amount)
        elif self.dataType == "Vector":
            mix1s, mix2s = VirtualVector3DList.createMultiple((mix1, 0), (mix2, 0))
            amount = VirtualDoubleList.getMaxRealLength(mix1s, mix2s, factors)
            return mixVectorLists(mix1s, mix2s, factors, amount)
        elif self.dataType == "Quaternion":
            mix1s, mix2s = VirtualQuaternionList.createMultiple((mix1, 0), (mix2, 0))
            amount = VirtualDoubleList.getMaxRealLength(factors)
            return mixQuaternionLists(mix1s, mix2s, factors, amount)
        elif self.dataType == "Matrix":
            mix1s, mix2s = VirtualMatrix4x4List.createMultiple((mix1, 0), (mix2, 0))
            amount = VirtualDoubleList.getMaxRealLength(mix1s, mix2s, factors)
            return mixMatrixLists(mix1s, mix2s, factors, amount)
        elif self.dataType == "Color":
            mix1s, mix2s = VirtualColorList.createMultiple((mix1, 0), (mix2, 0))
            amount = VirtualDoubleList.getMaxRealLength(mix1s, mix2s, factors)
            return mixColorLists(mix1s, mix2s, factors, amount)
        elif self.dataType == "Euler":
            mix1s, mix2s = VirtualEulerList.createMultiple((mix1, 0), (mix2, 0))
            amount = VirtualDoubleList.getMaxRealLength(mix1s, mix2s, factors)
            return mixEulerLists(mix1s, mix2s, factors, amount)

def getMixCode(dataType, mix1, mix2, factor):
    if dataType in ("Float", "Vector", "Quaternion"): return mix1 * (1 - factor) + mix2 * factor
    if dataType == "Matrix": return mix1.lerp(mix2, factor)
    if dataType == "Color": return Color([v1 * (1 - factor) + v2 * factor for v1, v2 in zip(mix1, mix2)])
    if dataType == "Euler": return mixEulers(mix1, mix2, factor)
