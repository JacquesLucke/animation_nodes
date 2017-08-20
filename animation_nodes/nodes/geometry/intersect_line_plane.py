import bpy
from mathutils import Vector
from ... data_structures import VirtualVector3DList
from ... base_types import AnimationNode, VectorizedSocket
from . c_utils import intersectLinePlaneList, intersectLinePlaneSingle

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

        props = ["useLineStartList", "useLineEndList",
        "usePlaneNormalList", "usePlanePointList"]

        self.newOutput(VectorizedSocket("Vector", props,
            ("Intersection", "intersection"),
            ("Intersections", "intersections")))
        self.newOutput(VectorizedSocket("Float", props,
            ("Parameter", "parameter"),
            ("Parameters", "parameters")))
        self.newOutput(VectorizedSocket("Boolean", props,
            ("Valid", "valid"),
            ("Valids", "valids")))

    def getExecutionFunctionName(self):
        useList = any((self.useLineStartList, self.useLineEndList,
        self.usePlaneNormalList, self.usePlanePointList))
        if useList:
            return "execute_List"
        else:
            return "execute_Single"

    def execute_List(self, linesStart, linesEnd, planesPoint, planesNormal):
        linesStart = VirtualVector3DList.fromListOrElement(linesStart, Vector((0, 0, 1)))
        linesEnd = VirtualVector3DList.fromListOrElement(linesEnd, Vector((0, 0, -1)))
        planesPoint = VirtualVector3DList.fromListOrElement(planesPoint, Vector((0, 0, 0)))
        planesNormal = VirtualVector3DList.fromListOrElement(planesNormal, Vector((0, 0, 1)))
        amount = VirtualVector3DList.getMaxRealLength(linesStart, linesEnd, planesPoint, planesNormal)
        return intersectLinePlaneList(amount, linesStart, linesEnd, planesPoint, planesNormal)

    def execute_Single(self, lineStart, lineEnd, planePoint, planeNormal):
        return intersectLinePlaneSingle(lineStart, lineEnd, planePoint, planeNormal)
