import bpy
from mathutils import Vector
from . c_utils import IntersectLineLine
from ... data_structures import VirtualVector3DList
from ... base_types import AnimationNode, VectorizedSocket

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
        if any((self.useFirstLineStartList, self.useFirstLineEndList,
        self.useSecondLineStartList, self.useSecondLineEndList)):
            return "execute_List"
        else:
            return "execute_Single"

    def execute_List(self, firstLinesStart, firstLinesEnd, secondLinesStart, secondLinesEnd):
        return self.getPoints(firstLinesStart, firstLinesEnd, secondLinesStart, secondLinesEnd, False)

    def execute_Single(self, firstLineStart, firstLineEnd, secondLineStart, secondLineEnd):
        result = self.getPoints(firstLineStart, firstLineEnd, secondLineStart, secondLineEnd, True)
        return [x[0] for x in result]

    def getPoints(self, firstLineStart, firstLineEnd, secondLineStart, secondLineEnd, singleElement):
        _firstLineStart = VirtualVector3DList.fromListOrElement(firstLineStart, Vector((1, 1, 0)))
        _firstLineEnd = VirtualVector3DList.fromListOrElement(firstLineEnd, Vector((-1, -1, 0)))
        _secondLineStart = VirtualVector3DList.fromListOrElement(secondLineStart, Vector((1, -1, 0)))
        _secondLineEnd = VirtualVector3DList.fromListOrElement(secondLineEnd, Vector((-1, 1, 0)))
        amount = VirtualVector3DList.getMaxRealLength(_firstLineStart, _firstLineEnd, _secondLineStart, _secondLineEnd)
        amount = 1 if singleElement else amount
        return IntersectLineLine(amount, _firstLineStart, _firstLineEnd, _secondLineStart, _secondLineEnd)
