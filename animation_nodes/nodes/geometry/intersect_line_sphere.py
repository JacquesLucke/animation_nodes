import bpy
from mathutils import Vector
from . c_utils import IntersectLineSphere
from ... data_structures import VirtualVector3DList, VirtualDoubleList
from ... base_types import AnimationNode, VectorizedSocket

class IntersectLineSphereNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_IntersectLineSphereNode"
    bl_label = "Intersect Line Sphere"
    bl_width_default = 200

    useLineStartList = VectorizedSocket.newProperty()
    useLineEndList = VectorizedSocket.newProperty()
    useSphereCenterList = VectorizedSocket.newProperty()
    useSphereRadiusList = VectorizedSocket.newProperty()

    def create(self):
        self.newInput(VectorizedSocket("Vector", "useLineStartList",
            ("Line Start", "lineStart", dict(value = (0, 0, 0))),
            ("Lines Start", "linesStart"),
            codeProperties = dict(default = (0, 0, 0))))
        self.newInput(VectorizedSocket("Vector", "useLineEndList",
            ("Line End", "lineEnd", dict(value = (0, 0, 2))),
            ("Lines End", "linesEnd"),
            codeProperties = dict(default = (0, 0, 2))))

        self.newInput(VectorizedSocket("Vector", "useSphereCenterList",
            ("Sphere Center", "sphereCenter", dict(value = (0, 0, 0))),
            ("Spheres Centers", "spheresCenters"),
            codeProperties = dict(default = (0, 0, 0))))
        self.newInput(VectorizedSocket("Float", "useSphereRadiusList",
            ("Sphere Radius", "sphereRadius", dict(value = 1)),
            ("Spheres Radii", "spheresRadii"),
            codeProperties = dict(default = 1)))

        self.newOutput(VectorizedSocket("Vector", ["useLineStartList", "useLineEndList", "useSphereCenterList", "useSphereRadiusList"],
            ("First Intersection", "firstIntersection"),
            ("First Intersections", "firstIntersections")))
        self.newOutput(VectorizedSocket("Vector", ["useLineStartList", "useLineEndList", "useSphereCenterList", "useSphereRadiusList"],
            ("Second Intersection", "secondIntersection"),
            ("Second Intersections", "secondIntersections")))

        self.newOutput(VectorizedSocket("Float", ["useLineStartList", "useLineEndList", "useSphereCenterList", "useSphereRadiusList"],
            ("First Intersection Parameter", "firstIntersectionParameter"),
            ("First Intersections Parameters", "firstIntersectionsParameters")))
        self.newOutput(VectorizedSocket("Float", ["useLineStartList", "useLineEndList", "useSphereCenterList", "useSphereRadiusList"],
            ("Second Intersection Parameter", "secondIntersectionParameter"),
            ("Second Intersections Parameters", "secondIntersectionsParameters")))

        self.newOutput(VectorizedSocket("Integer", ["useLineStartList", "useLineEndList", "useSphereCenterList", "useSphereRadiusList"],
            ("Number Of Intersections", "numberOfIntersections"),
            ("Number Of Intersections", "numberOfIntersections")))

    def getExecutionFunctionName(self):
        if any((self.useLineStartList, self.useLineEndList,
        self.useSphereCenterList, self.useSphereRadiusList)):
            return "execute_List"
        else:
            return "execute_Single"

    def execute_List(self, linesStart, linesEnd, spheresCenters, spheresRadii):
        return self.getIntersections(linesStart, linesEnd, spheresCenters, spheresRadii, False)

    def execute_Single(self, lineStart, lineEnd, sphereCenter, sphereRadius):
        return self.getIntersections(lineStart, lineEnd, sphereCenter, sphereRadius, True)

    def getIntersections(self, lineStart, lineEnd, sphereCenter, sphereRadius, singleElement):
        _lineStart = VirtualVector3DList.fromListOrElement(lineStart, Vector((1, 1, 0)))
        _lineEnd = VirtualVector3DList.fromListOrElement(lineEnd, Vector((-1, -1, 0)))
        _sphereCenter = VirtualVector3DList.fromListOrElement(sphereCenter, Vector((1, -1, 0)))
        _sphereRadius = VirtualDoubleList.fromListOrElement(sphereRadius, 1)
        amount = VirtualVector3DList.getMaxRealLength(_lineStart, _lineEnd, _sphereCenter, _sphereRadius)
        amount = 1 if singleElement else amount
        return IntersectLineSphere(amount, _lineStart, _lineEnd, _sphereCenter, _sphereRadius)
