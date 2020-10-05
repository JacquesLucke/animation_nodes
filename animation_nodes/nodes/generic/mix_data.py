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
    mixQuaternionLists,
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
            ("Factors", "factor")), dataIsModified = True)
        self.newInput(VectorizedSocket(self.dataType, ["useAList"], ("A", "a"), ("A", "a")))
        self.newInput(VectorizedSocket(self.dataType, ["useBList"], ("B", "b"), ("B", "b")))

        self.newOutput(VectorizedSocket(self.dataType, ["useAList", "useBList", "useFactorList"],
            ("Result", "result"), ("Results", "result")))

    def draw(self, layout):
        layout.prop(self, "clampFactor")

    def drawLabel(self):
        if any([self.useAList, self.useBList, self.useFactorList]):
            return nodeTypes[self.outputs[0].dataType.strip("List").rstrip()]
        return nodeTypes[self.outputs[0].dataType]

    def getExecutionCode(self, required):
        if any([self.useAList, self.useBList, self.useFactorList]):
            yield "result = self.execute_MixDataList(a, b, factor)"
        else:
            if self.clampFactor:
                yield "f = min(max(factor, 0.0), 1.0)"
            else:
                yield "f = factor"
            yield getMixCode(self.dataType, "a", "b", "f", "result")

    def execute_MixDataList(self, mix1, mix2, factor):
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

def getMixCode(dataType, mix1 = "a", mix2 = "b", factor = "f", result = "result"):
    if dataType in ("Float", "Vector", "Quaternion"): return f"{result} = {mix1} * (1 - {factor}) + {mix2} * {factor}"
    if dataType == "Matrix": return f"{result} = {mix1}.lerp({mix2}, {factor})"
    if dataType == "Color": return f"{result} = Color([v1 * (1 - {factor}) + v2 * {factor} for v1, v2 in zip({mix1}, {mix2})])"
    if dataType == "Euler": return f"{result} = animation_nodes.utils.math.mixEulers({mix1}, {mix2}, {factor})"

def mixMatrixLists(matricesA, matricesB, factors, amount):
    results = Matrix4x4List(length = amount)

    for i in range(amount):
        results[i] = matricesA[i].lerp(matricesB[i], factors[i])

    return results
