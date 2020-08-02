import bpy
from bpy.props import *
from ... utils.math import mixEulers
from ... data_structures import Color
from ... events import executionCodeChanged
from ... base_types import AnimationNode, VectorizedSocket

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
            ("Factors", "factors")))
        self.newInput(VectorizedSocket(self.dataType, ["useAList"], ("A", "a"), ("As", "as")))
        self.newInput(VectorizedSocket(self.dataType, ["useBList"], ("B", "b"), ("Bs", "bs")))

        self.newOutput(VectorizedSocket(self.dataType, ["useAList", "useBList", "useFactorList"],
            ("Result", "result"), ("Results", "results")))

    def draw(self, layout):
        layout.prop(self, "clampFactor")

    def drawLabel(self):
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
        return mixData(self.dataType, a, b, f)

def mixData(dataType, mix1, mix2, factor):
    if dataType in ("Float", "Vector", "Quaternion"): return mix1 * (1 - factor) + mix2 * factor
    if dataType == "Matrix": return mix1.lerp(mix2, factor)
    if dataType == "Color": return Color([v1 * (1 - factor) + v2 * factor for v1, v2 in zip(mix1, mix2)])
    if dataType == "Euler": return mixEulers(mix1, mix2, factor)
