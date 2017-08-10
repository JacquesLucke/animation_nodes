import bpy
from mathutils import Vector
from . c_utils import IntersectLinePlane
from ... data_structures import VirtualVector3DList
from ... base_types import AnimationNode, VectorizedSocket

class IntersectLinePlaneNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_IntersectLinePlaneNode"
    bl_label = "Intersect Line Plane"
    bl_width_default = 160

    useLineStartList = VectorizedSocket.newProperty()
    useLineEndList = VectorizedSocket.newProperty()
    usePlaneNormalList = VectorizedSocket.newProperty()
    usePlanePointList = VectorizedSocket.newProperty()

    def create(self):
        self.newInput(VectorizedSocket("Vector", "useLineStartList",
            ("Line Start", "lineStart", dict(value = (0, 0, 1))),
            ("Lines Start", "linesStart"),
            codeProperties = dict(default = (0, 0, 1))))
        self.newInput(VectorizedSocket("Vector", "useLineEndList",
            ("Line End", "lineEnd", dict(value = (0, 0, -1))),
            ("Lines End", "linesEnd"),
            codeProperties = dict(default = (0, 0, -1))))

        self.newInput(VectorizedSocket("Vector", "usePlanePointList",
            ("Plane Point", "planePoint", dict(value = (0, 0, 0))),
            ("Planes Point", "planesPoint"),
            codeProperties = dict(default = (0, 0, 0))))
        self.newInput(VectorizedSocket("Vector", "usePlaneNormalList",
            ("Plane Normal", "planeNormal", dict(value = (0, 0, 1))),
            ("Planes Normal", "planesNormal"),
            codeProperties = dict(default = (0, 0, 1))))

        self.newOutput(VectorizedSocket("Vector", ["useLineStartList", "useLineEndList", "usePlaneNormalList", "usePlanePointList"],
            ("Intersection", "intersection"),
            ("Intersections", "intersections")))
        self.newOutput(VectorizedSocket("Float", ["useLineStartList", "useLineEndList", "usePlaneNormalList", "usePlanePointList"],
            ("Parameter", "parameter"),
            ("Parameters", "parameters")))
        self.newOutput(VectorizedSocket("Boolean", ["useLineStartList", "useLineEndList", "usePlaneNormalList", "usePlanePointList"],
            ("Valid", "valid"),
            ("Valids", "valids")))

    def getExecutionFunctionName(self):
        if any((self.useLineStartList, self.useLineEndList,
        self.usePlaneNormalList, self.usePlanePointList)):
            return "execute_List"
        else:
            return "execute_Single"

    def execute_List(self, linesStart, linesEnd, planesPoint, planesNormal):
        return self.getIntersection(linesStart, linesEnd, planesPoint, planesNormal, False)

    def execute_Single(self, lineStart, lineEnd, planePoint, planeNormal):
        return self.getIntersection(lineStart, lineEnd, planePoint, planeNormal, True)

    def getIntersection(self, lineStart, lineEnd, planePoint, planeNormal, singleElement):
        _lineStart = VirtualVector3DList.fromListOrElement(lineStart, Vector((0, 0, 1)))
        _lineEnd = VirtualVector3DList.fromListOrElement(lineEnd, Vector((0, 0, -1)))
        _planePoint = VirtualVector3DList.fromListOrElement(planePoint, Vector((0, 0, 0)))
        _planeNormal = VirtualVector3DList.fromListOrElement(planeNormal, Vector((0, 0, 1)))
        amount = VirtualVector3DList.getMaxRealLength(_lineStart, _lineEnd, _planePoint, _planeNormal)
        amount = 1 if singleElement else amount
        return IntersectLinePlane(amount, _lineStart, _lineEnd, _planePoint, _planeNormal)
