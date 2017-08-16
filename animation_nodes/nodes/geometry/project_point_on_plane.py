import bpy
from mathutils import Vector
from . c_utils import ProjectPointOnPlane
from ... data_structures import VirtualVector3DList
from ... base_types import AnimationNode, VectorizedSocket

class ProjectPointOnPlaneNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_ProjectPointOnPlaneNode"
    bl_label = "Project Point on Plane"
    bl_width_default = 170
    searchTags = ["Distance Point to Plane", "Closest Point on Plane"]

    usePlanePointList = VectorizedSocket.newProperty()
    usePlaneNormalList = VectorizedSocket.newProperty()
    usePointList = VectorizedSocket.newProperty()

    def create(self):
        self.newInput(VectorizedSocket("Vector", "usePlanePointList",
            ("Plane Point", "planePoint", dict(value = (0, 0, 0))),
            ("Planes Points", "planesPoints"),
            codeProperties = dict(default = (0, 0, 0))))
        self.newInput(VectorizedSocket("Vector", "usePlaneNormalList",
            ("Plane Point", "planeNormal", dict(value = (0, 0, 1))),
            ("Planes Points", "planesNormals"),
            codeProperties = dict(default = (0, 0, 1))))

        self.newInput(VectorizedSocket("Vector", "usePointList",
            ("Point", "point", dict(value = (0, 0, 1))),
            ("Points", "points"),
            codeProperties = dict(default = (0, 0, 1))))

        self.newOutput(VectorizedSocket("Vector", ["usePlanePointList", "usePlaneNormalList", "usePointList"],
            ("Projection", "projection"),
            ("Projections", "projections")))
        self.newOutput(VectorizedSocket("Float", ["usePlanePointList", "usePlaneNormalList", "usePointList"],
            ("Signed Distance", "distance"),
            ("Signed Distances", "distances")))

    def getExecutionFunctionName(self):
        if any((self.usePlanePointList, self.usePlaneNormalList,
        self.usePointList)):
            return "execute_List"
        else:
            return "execute_Single"

    def execute_List(self, planesPoints, planesNormals, points):
        return self.getPoints(planesPoints, planesNormals, points, False)

    def execute_Single(self, planePoint, planeNormal, point):
        return self.getPoints(planePoint, planeNormal, point, True)

    def getPoints(self, planePoint, planeNormal, point, singleElement):
        _planePoint = VirtualVector3DList.fromListOrElement(planePoint, Vector((0, 0, 0)))
        _planeNormal = VirtualVector3DList.fromListOrElement(planeNormal, Vector((0, 0, 1)))
        _point = VirtualVector3DList.fromListOrElement(point, Vector((0, 0, 1)))
        amount = VirtualVector3DList.getMaxRealLength(_planePoint, _planeNormal, _point)
        amount = 1 if singleElement else amount
        return ProjectPointOnPlane(amount, _planePoint, _planeNormal, _point)
