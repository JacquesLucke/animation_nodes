import bpy
from mathutils import Vector
from ... data_structures import VirtualVector3DList
from ... base_types import AnimationNode, VectorizedSocket
from . c_utils import intersectPlanePlaneList, intersectPlanePlaneSingle

class IntersectPlanePlaneNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_IntersectPlanePlaneNode"
    bl_label = "Intersect Plane Plane"
    bl_width_default = 160

    usePlane1PointList = VectorizedSocket.newProperty()
    usePlane1NormalList = VectorizedSocket.newProperty()
    usePlane2PointList = VectorizedSocket.newProperty()
    usePlane2PointList = VectorizedSocket.newProperty()

    def create(self):
        self.newInput(VectorizedSocket("Vector", "usePlane1PointList",
            ("First Plane Point", "firstPlanePoint", dict(value = (0, 0, 0))),
            ("First Plane Points", "firstPlanePoints"),
            codeProperties = dict(default = (0, 0, 0))))
        self.newInput(VectorizedSocket("Vector", "usePlane1NormalList",
            ("First Plane Normal", "firstPlaneNormal", dict(value = (0, 0, 1))),
            ("First Plane Normals", "firstPlaneNormals"),
            codeProperties = dict(default = (0, 0, 1))))

        self.newInput(VectorizedSocket("Vector", "usePlane2PointList",
            ("Second Plane Point", "secondPlanePoint", dict(value = (0, 0, 0))),
            ("Second Plane Points", "secondPlanePoints"),
            codeProperties = dict(default = (0, 0, 0))))
        self.newInput(VectorizedSocket("Vector", "usePlane2PointList",
            ("Second Plane Normal", "secondPlaneNormal", dict(value = (1, 0, 0))),
            ("Second Plane Normals", "secondPlaneNormals"),
            codeProperties = dict(default = (1, 0, 0))))

        props = ["usePlane1PointList", "usePlane1NormalList",
        "usePlane2PointList", "usePlane2PointList"]

        self.newOutput(VectorizedSocket("Vector", props,
            ("Line Direction", "lineDirection"),
            ("Line Directions", "lineDirections")))
        self.newOutput(VectorizedSocket("Vector", props,
            ("Line Point", "linePoint"),
            ("Line Points", "linePoints")))
        self.newOutput(VectorizedSocket("Boolean", props,
            ("Valid", "valid"),
            ("Valids", "valids")))

    def getExecutionFunctionName(self):
        useList = any((self.usePlane1PointList, self.usePlane1NormalList,
        self.usePlane2PointList, self.usePlane2PointList))
        if useList:
            return "execute_List"
        else:
            return "execute_Single"

    def execute_List(self, firstPlanePoints, firstPlaneNormals,
        secondPlanePoints, secondPlaneNormals):
        firstPlanePoints = VirtualVector3DList.fromListOrElement(firstPlanePoints,
        Vector((0, 0, 0)))
        firstPlaneNormals = VirtualVector3DList.fromListOrElement(firstPlaneNormals,
        Vector((0, 0, 1)))
        secondPlanePoints = VirtualVector3DList.fromListOrElement(secondPlanePoints,
        Vector((0, 0, 0)))
        secondPlaneNormals = VirtualVector3DList.fromListOrElement(secondPlaneNormals,
        Vector((1, 0, 0)))
        amount = VirtualVector3DList.getMaxRealLength(firstPlanePoints, firstPlaneNormals,
        secondPlanePoints, secondPlaneNormals)
        return intersectPlanePlaneList(amount, firstPlanePoints, firstPlaneNormals,
        secondPlanePoints, secondPlaneNormals)

    def execute_Single(self, firstPlanePoint, firstPlaneNormal,
        secondPlanePoint, secondPlaneNormal):
        return intersectPlanePlaneSingle(firstPlanePoint, firstPlaneNormal,
        secondPlanePoint, secondPlaneNormal)
