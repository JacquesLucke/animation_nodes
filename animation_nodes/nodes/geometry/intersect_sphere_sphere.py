import bpy
from mathutils import Vector
from . c_utils import IntersectSphereSphere
from ... data_structures import VirtualVector3DList, VirtualDoubleList
from ... base_types import AnimationNode, VectorizedSocket

class IntersectSphereSphereNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_IntersectSphereSphereNode"
    bl_label = "Intersect Sphere Sphere"
    bl_width_default = 160

    useSphere1CenterList = VectorizedSocket.newProperty()
    useSphere1RadiusList = VectorizedSocket.newProperty()
    useSphere2CenterList = VectorizedSocket.newProperty()
    useSphere2RadiusList = VectorizedSocket.newProperty()

    def create(self):
        self.newInput(VectorizedSocket("Vector", "useSphere1CenterList",
            ("First Sphere Center", "firstSphereCenter", dict(value = (0, 0, -0.5))),
            ("First Spheres Centers", "firstSpheresCenters"),
            codeProperties = dict(default = (0, 0, -0.5))))
        self.newInput(VectorizedSocket("Float", "useSphere1RadiusList",
            ("First Sphere Radius", "firstSphereRadius", dict(value = 1)),
            ("First Spheres Radii", "firstSpheresRadii"),
            codeProperties = dict(default = 1)))

        self.newInput(VectorizedSocket("Vector", "useSphere2CenterList",
            ("Second Sphere Center", "secondSphereCenter", dict(value = (0, 0, 0.5))),
            ("Second Spheres Centers", "secondSpheresCenters"),
            codeProperties = dict(default = (0, 0, 0.5))))
        self.newInput(VectorizedSocket("Float", "useSphere2RadiusList",
            ("Second Sphere Radius", "secondSphereRadius", dict(value = 1)),
            ("Second Spheres Radii", "secondSpheresRadii"),
            codeProperties = dict(default = 1)))

        props = ["useSphere2CenterList", "useSphere2RadiusList",
        "useSphere1CenterList", "useSphere1RadiusList"]

        self.newOutput(VectorizedSocket("Vector", props,
            ("Circle Center", "circleCenter"),
            ("Circles Centers", "circlesCenters")))
        self.newOutput(VectorizedSocket("Vector", props,
            ("Circle Normal", "circleNormal"),
            ("Circles Normals", "circlesNormals")))
        self.newOutput(VectorizedSocket("Float", props,
            ("Circle Radius", "circleRadius"),
            ("Circles Radii", "circlesRadii")))

        self.newOutput(VectorizedSocket("Boolean", props,
            ("Valid", "valid"),
            ("Valids", "valids")))

    def getExecutionFunctionName(self):
        useList = any((self.useSphere2CenterList, self.useSphere2RadiusList,
        self.useSphere1CenterList, self.useSphere1RadiusList))
        if useList:
            return "execute_List"
        else:
            return "execute_Single"

    def execute_List(self, firstSpheresCenters, firstSpheresRadii, secondSpheresCenters, secondSpheresRadii):
        return self.getIntersections(firstSpheresCenters, firstSpheresRadii, secondSpheresCenters, secondSpheresRadii, False)

    def execute_Single(self, firstSphereCenter, firstSphereRadius, secondSphereCenter, secondSphereRadius):
        result = self.getIntersections(firstSphereCenter, firstSphereRadius, secondSphereCenter, secondSphereRadius, True)
        return [x[0] for x in result]

    def getIntersections(self, firstSphereCenter, firstSphereRadius, secondSphereCenter, secondSphereRadius, singleElement):
        _firstSphereCenter = VirtualVector3DList.fromListOrElement(firstSphereCenter, Vector((0, 0, -0.5)))
        _firstSphereRadius = VirtualDoubleList.fromListOrElement(firstSphereRadius, 1)
        _secondSphereCenter = VirtualVector3DList.fromListOrElement(secondSphereCenter, Vector((0, 0, 0.5)))
        _secondSphereRadius = VirtualDoubleList.fromListOrElement(secondSphereRadius, 1)
        amount = VirtualVector3DList.getMaxRealLength(_firstSphereCenter, _firstSphereRadius, _secondSphereCenter, _secondSphereRadius)
        amount = 1 if singleElement else amount
        return IntersectSphereSphere(amount, _firstSphereCenter, _firstSphereRadius, _secondSphereCenter, _secondSphereRadius)
