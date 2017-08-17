import bpy
from mathutils import Vector
from . c_utils import ProjectPointOnLine
from ... data_structures import VirtualVector3DList
from ... base_types import AnimationNode, VectorizedSocket

class ProjectPointOnLineNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_ProjectPointOnLineNode"
    bl_label = "Project Point on Line"
    bl_width_default = 160
    searchTags = ["Distance Point to Line", "Closest Point on Line"]

    useLineStartList = VectorizedSocket.newProperty()
    useLineEndList = VectorizedSocket.newProperty()
    usePointList = VectorizedSocket.newProperty()

    def create(self):
        self.newInput(VectorizedSocket("Vector", "useLineStartList",
            ("Line Start", "lineStart", dict(value = (0, 0, 0))),
            ("Lines Start", "linesStart"),
            codeProperties = dict(default = (0, 0, 0))))
        self.newInput(VectorizedSocket("Vector", "useLineEndList",
            ("Line End", "lineEnd", dict(value = (1, 0, 0))),
            ("Lines End", "linesEnd"),
            codeProperties = dict(default = (1, 0, 0))))

        self.newInput(VectorizedSocket("Vector", "usePointList",
            ("Point", "point", dict(value = (1, 1, 0))),
            ("Points", "points"),
            codeProperties = dict(default = (1, 1, 0))))

        props = ["useLineStartList", "useLineEndList", "usePointList"]

        self.newOutput(VectorizedSocket("Vector", props,
            ("Projection", "projection"),
            ("Projections", "projections")))
        self.newOutput(VectorizedSocket("Float", props,
            ("Parameter", "parameter"),
            ("Parameters", "parameters")))
        self.newOutput(VectorizedSocket("Float", props,
            ("Distance", "distance"),
            ("Distances", "distances")))

    def getExecutionFunctionName(self):
        useList = any((self.useLineStartList, self.useLineEndList,
        self.usePointList))
        if useList:
            return "execute_List"
        else:
            return "execute_Single"

    def execute_List(self, linesStart, linesEnd, points):
        return self.getPoints(linesStart, linesEnd, points, False)

    def execute_Single(self, lineStart, lineEnd, point):
        result = self.getPoints(lineStart, lineEnd, point, True)
        return [x[0] for x in result]

    def getPoints(self, lineStart, lineEnd, point, singleElement):
        _lineStart = VirtualVector3DList.fromListOrElement(lineStart, Vector((0, 0, 0)))
        _lineEnd = VirtualVector3DList.fromListOrElement(lineEnd, Vector((1, 0, 0)))
        _point = VirtualVector3DList.fromListOrElement(point, Vector((1, 1, 0)))
        amount = VirtualVector3DList.getMaxRealLength(_lineStart, _lineEnd, _point)
        amount = 1 if singleElement else amount
        return ProjectPointOnLine(amount, _lineStart, _lineEnd, _point)
