import bpy
from mathutils import Vector
from . c_utils import IntersectSpherePlane
from ... data_structures import VirtualVector3DList, VirtualDoubleList
from ... base_types import AnimationNode, VectorizedSocket

class IntersectSpherePlaneNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_IntersectSpherePlaneNode"
    bl_label = "Intersect Sphere Plane"
    bl_width_default = 160

    useSphereCenterList = VectorizedSocket.newProperty()
    useSphereRadiusList = VectorizedSocket.newProperty()
    usePlanePointList = VectorizedSocket.newProperty()
    usePlaneNormalList = VectorizedSocket.newProperty()

    def create(self):
        self.newInput(VectorizedSocket("Vector", "useSphereCenterList",
            ("Sphere Center", "sphereCenter", dict(value = (0, 0, 0))),
            ("Spheres Centers", "spheresCenters"),
            codeProperties = dict(default = (0, 0, 0))))
        self.newInput(VectorizedSocket("Float", "useSphereRadiusList",
            ("Sphere Radius", "sphereRadius", dict(value = 1)),
            ("Spheres Radii", "spheresRadii"),
            codeProperties = dict(default = 1)))

        self.newInput(VectorizedSocket("Vector", "usePlanePointList",
            ("Plane Point", "planePoint", dict(value = (0, 0, 0))),
            ("Planes Points", "planesPoints"),
            codeProperties = dict(default = (0, 0, 0))))
        self.newInput(VectorizedSocket("Vector", "usePlaneNormalList",
            ("Plane Normal", "planeNormal", dict(value = (0, 0, 1))),
            ("Planes Normals", "planesNormals"),
            codeProperties = dict(default = (0, 0, 1))))

        props = ["usePlanePointList", "usePlaneNormalList",
        "useSphereCenterList", "useSphereRadiusList"]

        self.newOutput(VectorizedSocket("Vector", props,
            ("Circle Center", "circleCenter"),
            ("Circles Centers", "circlesCenters")))
        self.newOutput(VectorizedSocket("Float", props,
            ("Circle Radius", "circleRadius"),
            ("Circles Radii", "circlesRadii")))

        self.newOutput(VectorizedSocket("Boolean", props,
            ("Valid", "valid"),
            ("Valids", "valids")))

    def getExecutionFunctionName(self):
        useList =  any((self.usePlanePointList, self.usePlaneNormalList,
        self.useSphereCenterList, self.useSphereRadiusList))
        if useList:
            return "execute_List"
        else:
            return "execute_Single"

    def execute_List(self, spheresCenters, spheresRadii, planesPoints, planesNormals):
        return self.getIntersections(spheresCenters, spheresRadii, planesPoints, planesNormals, False)

    def execute_Single(self, sphereCenter, sphereRadius, planePoint, planeNormal):
        result = self.getIntersections(sphereCenter, sphereRadius, planePoint, planeNormal, True)
        return [x[0] for x in result]

    def getIntersections(self, sphereCenter, sphereRadius, planePoint, planeNormal, singleElement):
        _sphereCenter = VirtualVector3DList.fromListOrElement(sphereCenter, Vector((0, 0, 0)))
        _sphereRadius = VirtualDoubleList.fromListOrElement(sphereRadius, 1)
        _planePoint = VirtualVector3DList.fromListOrElement(planePoint, Vector((0, 0, 0)))
        _planeNormal = VirtualVector3DList.fromListOrElement(planeNormal, Vector((0, 0, 1)))
        amount = VirtualVector3DList.getMaxRealLength(_sphereCenter, _sphereRadius, _planePoint, _planeNormal)
        amount = 1 if singleElement else amount
        return IntersectSpherePlane(amount, _sphereCenter, _sphereRadius, _planePoint, _planeNormal)
