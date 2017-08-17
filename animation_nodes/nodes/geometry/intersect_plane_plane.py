import bpy
from mathutils import Vector
from . c_utils import IntersectPlanePlane
from ... data_structures import VirtualVector3DList
from ... base_types import AnimationNode, VectorizedSocket

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
            ("First Planes Points", "firstPlanesPoints"),
            codeProperties = dict(default = (0, 0, 0))))
        self.newInput(VectorizedSocket("Vector", "usePlane1NormalList",
            ("First Plane Normal", "firstPlaneNormal", dict(value = (0, 0, 1))),
            ("First Planes Normals", "firstPlanesNormals"),
            codeProperties = dict(default = (0, 0, 1))))

        self.newInput(VectorizedSocket("Vector", "usePlane2PointList",
            ("Second Plane Point", "secondPlanePoint", dict(value = (0, 0, 0))),
            ("Second Planes Points", "secondPlanesPoints"),
            codeProperties = dict(default = (0, 0, 0))))
        self.newInput(VectorizedSocket("Vector", "usePlane2PointList",
            ("Second Plane Normal", "secondPlaneNormal", dict(value = (1, 0, 0))),
            ("Second Planes Normals", "secondPlanesNormals"),
            codeProperties = dict(default = (1, 0, 0))))

        props = ["usePlane1PointList", "usePlane1NormalList",
        "usePlane2PointList", "usePlane2PointList"]

        self.newOutput(VectorizedSocket("Vector", props,
            ("Line Direction", "lineDirection"),
            ("Lines Directions", "linesDirections")))
        self.newOutput(VectorizedSocket("Vector", props,
            ("Line Point", "linePoint"),
            ("Lines Points", "linesPoints")))
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

    def execute_List(self, firstPlanesPoints, firstPlanesNormals, secondPlanesPoints, secondPlanesNormals):
        return self.getLine(firstPlanesPoints, firstPlanesNormals, secondPlanesPoints, secondPlanesNormals, False)

    def execute_Single(self, firstPlanePoint, firstPlaneNormal, secondPlanePoint, secondPlaneNormal):
        result = self.getLine(firstPlanePoint, firstPlaneNormal, secondPlanePoint, secondPlaneNormal, True)
        return [x[0] for x in result]

    def getLine(self, firstPlanePoint, firstPlaneNormal, secondPlanePoint, secondPlaneNormal, singleElement):
        _firstPlanePoint = VirtualVector3DList.fromListOrElement(firstPlanePoint, Vector((0, 0, 0)))
        _firstPlaneNormal = VirtualVector3DList.fromListOrElement(firstPlaneNormal, Vector((0, 0, 1)))
        _secondPlanePoint = VirtualVector3DList.fromListOrElement(secondPlanePoint, Vector((0, 0, 0)))
        _secondPlaneNormal = VirtualVector3DList.fromListOrElement(secondPlaneNormal, Vector((1, 0, 0)))
        amount = VirtualVector3DList.getMaxRealLength(_firstPlanePoint, _firstPlaneNormal, _secondPlanePoint, _secondPlaneNormal)
        amount = 1 if singleElement else amount
        return IntersectPlanePlane(amount, _firstPlanePoint, _firstPlaneNormal, _secondPlanePoint, _secondPlaneNormal)
