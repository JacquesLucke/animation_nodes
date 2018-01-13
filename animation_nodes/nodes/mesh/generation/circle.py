import bpy
from .... base_types import AnimationNode, VectorizedSocket
from .... data_structures import VirtualDoubleList, VirtualLongList, VirtualBooleanList
from .... algorithms.mesh_generation.circle import getCircleMesh, getCircleMeshList

class Circle(bpy.types.Node, AnimationNode):
    bl_idname = "an_CircleNode"
    bl_label = "Circle"
    bl_width_default = 160

    useRadialLoopsList = VectorizedSocket.newProperty()
    useInnerLoopsList = VectorizedSocket.newProperty()
    useOuterRadiusList = VectorizedSocket.newProperty()
    useInnerRadiusList = VectorizedSocket.newProperty()
    useStartAngleList = VectorizedSocket.newProperty()
    useEndAngleList = VectorizedSocket.newProperty()
    useMergeStartEndList = VectorizedSocket.newProperty()
    useMergeCenterList = VectorizedSocket.newProperty()

    def create(self):
        self.newInput(VectorizedSocket("Integer", "useRadialLoopsList",
            ("Radial Loops", "radialLoops", dict(value = 10, minValue = 3)),
            ("Radial Loops", "radialLoops"),
            codeProperties = dict(default = 10)))
        self.newInput(VectorizedSocket("Integer", "useInnerLoopsList",
            ("Inner Loops", "innerLoops", dict(value = 0, minValue = 0)),
            ("Inner Loops", "innerLoops"),
            codeProperties = dict(default = 0)))

        self.newInput(VectorizedSocket("Float", "useOuterRadiusList",
            ("Outer Radius", "outerRadius", dict(value = 1)),
            ("Outer Radii", "outerRadii"),
            codeProperties = dict(default = 1)))
        self.newInput(VectorizedSocket("Float", "useInnerRadiusList",
            ("Inner Radius", "innerRadii", dict(value = 0.5)),
            ("Inner Radii", "innerRadii"),
            codeProperties = dict(default = 0.5)))
        self.newInput(VectorizedSocket("Float", "useStartAngleList",
            ("Start Angle", "startAngle", dict(value = 0)),
            ("Start Angles", "startAngles"),
            codeProperties = dict(default = 0)))
        self.newInput(VectorizedSocket("Float", "useEndAngleList",
            ("End Angle", "endAngle", dict(value = 5)),
            ("End Angles", "endAngles"),
            codeProperties = dict(default = 5)))

        self.newInput(VectorizedSocket("Boolean", "useMergeStartEndList",
            ("Merge Start End", "mergeStartEnd", dict(value = True)),
            ("Merge Start Ends", "mergeStartEnds"),
            codeProperties = dict(default = True)))
        self.newInput(VectorizedSocket("Boolean", "useMergeCenterList",
            ("Merge Center", "mergeCenter", dict(value = True)),
            ("Merge Centers", "mergeCenters"),
            codeProperties = dict(default = True)))

        props = ["useRadialLoopsList", "useInnerLoopsList",
                 "useOuterRadiusList", "useInnerRadiusList",
                 "useStartAngleList", "useEndAngleList",
                 "useMergeStartEndList", "useMergeCenterList"]

        self.newOutput(VectorizedSocket("Mesh", props,
            ("Mesh", "Mesh"),
            ("Meshes", "Meshes")))

    def getExecutionFunctionName(self):
        useList = any((self.useRadialLoopsList, self.useInnerLoopsList,
                       self.useOuterRadiusList, self.useInnerRadiusList,
                       self.useStartAngleList, self.useEndAngleList,
                       self.useMergeStartEndList, self.useMergeCenterList))
        if useList:
            return "execute_List"
        else:
            return "execute_Single"

    def execute_List(self, radialLoops, innerLoops, outerRadii, innerRadii,
                     startAngles, endAngles, mergeStartEnds, mergeCenters):
        radialLoops = VirtualLongList.fromListOrElement(radialLoops, 10)
        innerLoops = VirtualLongList.fromListOrElement(innerLoops, 0)
        outerRadii = VirtualDoubleList.fromListOrElement(outerRadii, 1)
        innerRadii = VirtualDoubleList.fromListOrElement(innerRadii, 0.5)
        startAngles = VirtualDoubleList.fromListOrElement(startAngles, 0)
        endAngles = VirtualDoubleList.fromListOrElement(endAngles, 5)
        mergeStartEnds = VirtualBooleanList.fromListOrElement(mergeStartEnds, True)
        mergeCenters = VirtualBooleanList.fromListOrElement(mergeCenters, True)
        amount = VirtualLongList.getMaxRealLength(radialLoops, innerLoops,
                                                  outerRadii, innerRadii,
                                                  startAngles, endAngles,
                                                  mergeStartEnds, mergeCenters)
        return getCircleMeshList(amount, radialLoops, innerLoops,
                                   outerRadii, innerRadii, startAngles,
                                   endAngles, mergeStartEnds, mergeCenters)

    def execute_Single(self, radialLoops, innerLoops, outerRadius, innerRadius,
                             startAngle, endAngle, mergeStartEnd, mergeCenter):
        return getCircleMesh(radialLoops, innerLoops, outerRadius, innerRadius,
                               startAngle, endAngle, mergeStartEnd, mergeCenter)
