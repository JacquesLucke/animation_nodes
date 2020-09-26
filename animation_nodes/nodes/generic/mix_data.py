import bpy
from bpy.props import *
from ... utils.math import mixEulers
from ... events import executionCodeChanged
from ... base_types import AnimationNode, VectorizedSocket
from . c_utils import mixDoubleLists, mixVectorLists, mixQuaternionLists, mixColorLists
from ... data_structures import (
    Color,
    EulerList,
    Matrix4x4List,
    QuaternionList,
    VirtualColorList,
    VirtualEulerList,
    VirtualDoubleList,
    VirtualVector3DList,
    VirtualMatrix4x4List
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

    useAList: VectorizedSocket.newProperty()
    useBList: VectorizedSocket.newProperty()
    useFactorList: VectorizedSocket.newProperty()

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
        if self.dataType == "Float":
            factors = VirtualDoubleList.create(factor, 0)
            mix1s = VirtualDoubleList.create(mix1, 0)
            mix2s = VirtualDoubleList.create(mix2, 0)
            return mixDoubleLists(mix1s, mix2s, factors)
        elif self.dataType == "Vector":
            factors = VirtualDoubleList.create(factor, 0)
            mix1s = VirtualVector3DList.create(mix1, 0)
            mix2s = VirtualVector3DList.create(mix2, 0)
            return mixVectorLists(mix1s, mix2s, factors)
        elif self.dataType == "Quaternion":
            factors = VirtualDoubleList.create(factor, 0)
            mix1s = QuaternionList.fromValue(mix1)
            mix2s = QuaternionList.fromValue(mix2)
            return mixQuaternionLists(mix1s, mix2s, factors)
        elif self.dataType == "Matrix":
            factors = VirtualDoubleList.create(factor, 0)
            mix1s = VirtualMatrix4x4List.create(mix1, 0)
            mix2s = VirtualMatrix4x4List.create(mix2, 0)
            return mixMatrixLists(mix1s, mix2s, factors)
        elif self.dataType == "Color":
            factors = VirtualDoubleList.create(factor, 0)
            mix1s = VirtualColorList.create(mix1, 0)
            mix2s = VirtualColorList.create(mix2, 0)
            return mixColorLists(mix1s, mix2s, factors)
        elif self.dataType == "Euler":
            factors = VirtualDoubleList.create(factor, 0)
            mix1s = VirtualEulerList.create(mix1, 0)
            mix2s = VirtualEulerList.create(mix2, 0)
            return mixEulerLists(mix1s, mix2s, factors)

def getMixCode(dataType, mix1, mix2, factor):
    if dataType in ("Float", "Vector", "Quaternion"): return mix1 * (1 - factor) + mix2 * factor
    if dataType == "Matrix": return mix1.lerp(mix2, factor)
    if dataType == "Color": return Color([v1 * (1 - factor) + v2 * factor for v1, v2 in zip(mix1, mix2)])
    if dataType == "Euler": return mixEulers(mix1, mix2, factor)

def mixMatrixLists(matricesA, matricesB, influences):
    amount = VirtualDoubleList.getMaxRealLength(matricesA, matricesB, influences)
    results = Matrix4x4List(length = amount)
    for i in range(amount):
        results[i] = matricesA[i].lerp(matricesB[i], influences[i])

    return results

def mixEulerLists(eulersA, eulersB, influences):
    amount = VirtualDoubleList.getMaxRealLength(eulersA, eulersB, influences)
    results = EulerList(length = amount)
    for i in range(amount):
        results[i] = mixEulers(eulersA[i], eulersB[i], influences[i])

    return results
