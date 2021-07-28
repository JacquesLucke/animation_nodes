import bpy
from bpy.props import *
from ... events import propertyChanged
from ... data_structures cimport BaseFalloff
from .. falloff . mix_falloffs import MixFalloffs
from ... math cimport Vector3, setVector3, distanceVec3
from ... base_types import AnimationNode, VectorizedSocket
from ... data_structures import VirtualVector3DList, VirtualDoubleList

mixListTypeItems = [
    ("MAX", "Max", "", "NONE", 0),
    ("ADD", "Add", "", "NONE", 1),
]

class PointDistanceFalloffNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_PointDistanceFalloffNode"
    bl_label = "Point Distance Falloff"

    __annotations__ = {}

    __annotations__["mixListType"] = EnumProperty(name = "Mix List Type", default = "MAX",
        items = mixListTypeItems, update = propertyChanged)

    __annotations__["useOriginList"] = VectorizedSocket.newProperty()

    __annotations__["useSizeList"] = VectorizedSocket.newProperty()

    __annotations__["useFalloffWidthList"] = VectorizedSocket.newProperty()

    def create(self):
        self.newInput(VectorizedSocket("Vector", "useOriginList",
            ("Origin", "origin"), ("Origins", "origin")))
        self.newInput(VectorizedSocket("Float", "useSizeList",
            ("Size", "size"), ("Sizes", "size")))
        self.newInput(VectorizedSocket("Float", "useFalloffWidthList",
            ("Falloff Width", "falloffWidth", dict(value = 4)),
            ("Falloff Widths", "falloffWidth")))

        self.newOutput("Falloff", "Falloff", "falloff")

    def draw(self, layout):
        if any([self.useOriginList, self.useSizeList, self.useFalloffWidthList]):
            layout.prop(self, "mixListType", text = "")

    def getExecutionFunctionName(self):
        if any([self.useOriginList, self.useSizeList, self.useFalloffWidthList]):
            return "executeList"
        else:
            return "executeSingle"

    def executeSingle(self, origin, size, falloffWidth):
        return PointDistanceFalloff(origin, size, falloffWidth)

    def executeList(self, origin, size, falloffWidth):
        _origins = VirtualVector3DList.create(origin, (0,0,0))
        _sizes = VirtualDoubleList.create(size, 0)
        _widths = VirtualDoubleList.create(falloffWidth, 4)
        amount = VirtualVector3DList.getMaxRealLength(_origins, _sizes, _widths)
        falloffs = [self.executeSingle(_origins[i], _sizes[i], _widths[i]) for i in range(amount)]
        return MixFalloffs(falloffs, self.mixListType)


cdef class PointDistanceFalloff(BaseFalloff):
    cdef:
        Vector3 origin
        float factor
        float minDistance, maxDistance

    def __cinit__(self, vector, float size, float falloffWidth):
        if falloffWidth < 0:
            size += falloffWidth
            falloffWidth = -falloffWidth
        self.minDistance = size
        self.maxDistance = size + falloffWidth

        if self.minDistance == self.maxDistance:
            self.minDistance -= 0.00001
        self.factor = 1 / (self.maxDistance - self.minDistance)
        setVector3(&self.origin, vector)

        self.dataType = "LOCATION"
        self.clamped = True

    cdef float evaluate(self, void *value, Py_ssize_t index):
        return calcDistance(self, <Vector3*>value)

    cdef void evaluateList(self, void *values, Py_ssize_t startIndex,
                           Py_ssize_t amount, float *target):
        cdef Py_ssize_t i
        for i in range(amount):
            target[i] = calcDistance(self, <Vector3*>values + i)


cdef inline float calcDistance(PointDistanceFalloff self, Vector3 *v):
    cdef float distance = distanceVec3(&self.origin, v)
    if distance <= self.minDistance: return 1
    if distance <= self.maxDistance: return 1 - (distance - self.minDistance) * self.factor
    return 0
