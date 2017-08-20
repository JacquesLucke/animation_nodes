import bpy
from mathutils import Vector
from ... data_structures import VirtualVector3DList
from ... base_types import AnimationNode, VectorizedSocket
from . c_utils import intersectLineLineList, intersectLineLineSingle

class IntersectLineLineNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_IntersectLineLineNode"
    bl_label = "Intersect Line Line"
    bl_width_default = 160
    searchTags = ["Nearest Points on 2 Lines"]

    useFirstLineStartList = VectorizedSocket.newProperty()
    useFirstLineEndList = VectorizedSocket.newProperty()
    useSecondLineStartList = VectorizedSocket.newProperty()
    useSecondLineEndList = VectorizedSocket.newProperty()

    def create(self):
        self.newInput(VectorizedSocket("Vector", "useFirstLineStartList",
            ("First Line Start", "firstLineStart", dict(value = (1, 1, 0))),
            ("First Lines Start", "firstLinesStart"),
            codeProperties = dict(default = (1, 1, 0))))
        self.newInput(VectorizedSocket("Vector", "useFirstLineEndList",
            ("First Line End", "firstLineEnd", dict(value = (-1, -1, 0))),
            ("First Lines End", "firstLinesEnd"),
            codeProperties = dict(default = (-1, -1, 0))))

        self.newInput(VectorizedSocket("Vector", "useSecondLineStartList",
            ("Second Line Start", "secondLineStart", dict(value = (1, -1, 0))),
            ("Second Lines Start", "secondLinesStart"),
            codeProperties = dict(default = (1, -1, 0))))
        self.newInput(VectorizedSocket("Vector", "useSecondLineEndList",
            ("Second Line End", "secondLineEnd", dict(value = (-1, 1, 0))),
            ("Second Lines End", "secondLinesEnd"),
            codeProperties = dict(default = (-1, 1, 0))))

        props = ["useFirstLineStartList", "useFirstLineEndList",
        "useSecondLineStartList", "useSecondLineEndList"]

        self.newOutput(VectorizedSocket("Vector", props,
            ("First Line Nearest Point", "firstNearestPoint"),
            ("First Lines Nearest Points", "firstNearestPoints")))
        self.newOutput(VectorizedSocket("Vector", props,
            ("Second Line Nearest Point", "secondNearestPoint"),
            ("Second Lines Nearest Points", "secondNearestPoints")))

        self.newOutput(VectorizedSocket("Float", props,
            ("First Line Parameter", "firstParameter"),
            ("First Lines Parameters", "firstParameters")))
        self.newOutput(VectorizedSocket("Float", props,
            ("Second Line Parameter", "secondParameter"),
            ("Second Lines Parameters", "secondParameters")))

        self.newOutput(VectorizedSocket("Boolean", props,
            ("Valid", "valid"),
            ("Valids", "valids")))

    def getExecutionFunctionName(self):
        useList = any((self.useFirstLineStartList, self.useFirstLineEndList,
        self.useSecondLineStartList, self.useSecondLineEndList))
        if useList:
            return "execute_List"
        else:
            return "execute_Single"

    def execute_List(self, firstLinesStart, firstLinesEnd, secondLinesStart, secondLinesEnd):
        firstLinesStart = VirtualVector3DList.fromListOrElement(firstLinesStart, Vector((1, 1, 0)))
        firstLinesEnd = VirtualVector3DList.fromListOrElement(firstLinesEnd, Vector((-1, -1, 0)))
        secondLinesStart = VirtualVector3DList.fromListOrElement(secondLinesStart, Vector((1, -1, 0)))
        secondLinesEnd = VirtualVector3DList.fromListOrElement(secondLinesEnd, Vector((-1, 1, 0)))
        amount = VirtualVector3DList.getMaxRealLength(firstLinesStart, firstLinesEnd,
        secondLinesStart, secondLinesEnd)
        return intersectLineLineList(amount, firstLinesStart, firstLinesEnd,
        secondLinesStart, secondLinesEnd)

    def execute_Single(self, firstLineStart, firstLineEnd, secondLineStart, secondLineEnd):
        return intersectLineLineSingle(firstLineStart, firstLineEnd, secondLineStart, secondLineEnd)
