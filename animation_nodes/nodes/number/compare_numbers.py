import bpy
from bpy.props import *
from ... events import executionCodeChanged
from ... data_structures import VirtualDoubleList
from ... base_types import AnimationNode, VectorizedSocket
from . c_utils import (
    compareNumbers_Equal,
    compareNumbers_NotEqual,
    compareNumbers_LessThan,
    compareNumbers_GreaterThan,
    compareNumbers_LessThanOrEqual,
    compareNumbers_GreaterThanOrEqual,
)

compareTypeItems = (
    ("A=B", "A = B", "", "NONE", 0),
    ("A!=B", "A != B", "", "NONE", 1),
    ("A<B", "A < B", "", "NONE", 2),
    ("A>B", "A > B", "", "NONE", 3),
    ("A<=B", "A <= B", "", "NONE", 4),
    ("A>=B", "A >= B", "", "NONE", 5),
)

class CompareNumbersNode(AnimationNode, bpy.types.Node):
    bl_idname = "an_CompareNumbersNode"
    bl_label = "Compare Numbers"
    dynamicLabelType = "HIDDEN_ONLY"

    useAList: VectorizedSocket.newProperty()
    useBList: VectorizedSocket.newProperty()

    compareType: EnumProperty(name = "Compare Type",
        items = compareTypeItems, update = executionCodeChanged)

    def create(self):
        self.newInput(VectorizedSocket("Float", "useAList", ("A", "a"), ("A", "a")))
        self.newInput(VectorizedSocket("Float", "useBList", ("B", "b"), ("B", "b")))

        self.newOutput(VectorizedSocket("Boolean", ("useAList", "useBList"),
            ("Result", "result"), ("Result", "result")))

    def draw(self, layout):
        layout.prop(self, "compareType", text = "Type")

    def drawLabel(self):
        label = next(item[1] for item in compareTypeItems if self.compareType == item[0])
        if getattr(self.socketA, "isUnlinked", False):
            label = label.replace("A", str(round(self.socketA.value, 4)))
        if getattr(self.socketB, "isUnlinked", False):
            label = label.replace("B", str(round(self.socketB.value, 4)))
        return label

    def getExecutionCode(self, required):
        if any((self.useAList, self.useBList)):
            yield "result = self.executeList(a, b)"
        else:
            yield from self.executeSingle()

    def executeSingle(self):
        if self.compareType == "A=B":
            yield "result = a == b"
        if self.compareType == "A!=B":
            yield "result = a != b"
        if self.compareType == "A<B":
            yield "result = a < b"
        if self.compareType == "A>B":
            yield "result = a > b"
        if self.compareType == "A<=B":
            yield "result = a <= b"
        if self.compareType == "A>=B":
            yield "result = a >= b"

    def executeList(self, a, b):
        virtualA, virtualB = VirtualDoubleList.createMultiple((a, 0), (b, 0))
        amount = VirtualDoubleList.getMaxRealLength(virtualA, virtualB)
        if self.compareType == "A=B":
            return compareNumbers_Equal(virtualA, virtualB, amount)
        if self.compareType == "A!=B":
            return compareNumbers_NotEqual(virtualA, virtualB, amount)
        if self.compareType == "A<B":
            return compareNumbers_LessThan(virtualA, virtualB, amount)
        if self.compareType == "A>B":
            return compareNumbers_GreaterThan(virtualA, virtualB, amount)
        if self.compareType == "A<=B":
            return compareNumbers_LessThanOrEqual(virtualA, virtualB, amount)
        if self.compareType == "A>=B":
            return compareNumbers_GreaterThanOrEqual(virtualA, virtualB, amount)

    @property
    def socketA(self):
        return self.inputs.get("A")

    @property
    def socketB(self):
        return self.inputs.get("B")
