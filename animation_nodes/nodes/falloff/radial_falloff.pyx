import bpy
import cython
from ... base_types import AnimationNode
from libc.math cimport atan2, floor, M_PI
from ... data_structures cimport BaseFalloff
from ... math cimport (
    Vector3, setVector3, subVec3, Matrix3,
    normalizeVec3_InPlace, scalarTripleProduct,
    dotVec3, scaleVec3, addVec3, angleVec3,
)

class RadialFalloffNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_RadialFalloffNode"
    bl_label = "Radial Falloff"

    def create(self):
        self.newInput("Vector", "Origin", "origin")
        self.newInput("Vector", "Normal", "normal", value = (0, 0, 1))
        self.newInput("Float", "Phase", "phase")
        self.newOutput("Falloff", "Falloff", "falloff")

    def execute(self, origin, normal, phase):
        return RadialFalloff(origin, normal, phase)


cdef class RadialFalloff(BaseFalloff):
    cdef:
        Vector3 origin
        Vector3 normal
        float phase
        Vector3 xBasisProjection

    def __cinit__(self, origin, normal, float phase):
        setVector3(&self.origin, origin)
        setVector3(&self.normal, normal)
        normalizeVec3_InPlace(&self.normal)
        self.phase = phase
        self.dataType = "LOCATION"

        # In the 2D case, where the normal is aligned with one of the global axis,
        # we just compute the angle to one of the global axis lying on the plane.
        # In the 3D case, we need some arbitrary basis on the plane, we chose this
        # basis as the projection of the global x basis vector on the plane.
        cdef Vector3 xBasis
        xBasis.x, xBasis.y, xBasis.z = 1, 0, 0
        projectPointOnOriginPlane(&self.normal, &xBasis, &self.xBasisProjection)

    cdef float evaluate(self, void *value, Py_ssize_t index):
        cdef Vector3 position
        subVec3(&position, <Vector3 *>value, &self.origin)

        if self.normal.x == 0 and self.normal.y == 0:
            return self.getRadialValue2D(position.x, position.y)
        elif self.normal.x == 0 and self.normal.z == 0:
            return self.getRadialValue2D(position.x, position.z)
        elif self.normal.y == 0 and self.normal.z == 0:
            return self.getRadialValue2D(position.y, position.z)
        else:
            return self.getRadialValue3D(&position)

    cdef void evaluateList(self, void *values, Py_ssize_t startIndex,
                           Py_ssize_t amount, float *target):
        cdef Py_ssize_t i
        cdef Vector3 position

        if self.normal.x == 0 and self.normal.y == 0:
            for i in range(amount):
                subVec3(&position, <Vector3 *>values + i, &self.origin)
                target[i] = self.getRadialValue2D(position.x, position.y)
        elif self.normal.x == 0 and self.normal.z == 0:
            for i in range(amount):
                subVec3(&position, <Vector3 *>values + i, &self.origin)
                target[i] = self.getRadialValue2D(position.x, position.z)
        elif self.normal.y == 0 and self.normal.z == 0:
            for i in range(amount):
                subVec3(&position, <Vector3 *>values + i, &self.origin)
                target[i] = self.getRadialValue2D(position.y, position.z)
        else:
            for i in range(amount):
                subVec3(&position, <Vector3 *>values + i, &self.origin)
                target[i] = self.getRadialValue3D(&position)

    @cython.cdivision(True)
    cdef float getRadialValue2D(self, float x, float y):
        cdef double angle = atan2(y, x)
        if angle < 0: angle += 2 * M_PI
        cdef double factor = angle / (2 * M_PI) - self.phase
        return factor - floor(factor)

    @cython.cdivision(True)
    cdef float getRadialValue3D(self, Vector3 *position):
        cdef Vector3 projection
        projectPointOnOriginPlane(&self.normal, position, &projection)

        cdef float angle = angleVec3(&projection, &self.xBasisProjection)
        
        cdef float signIndicator = scalarTripleProduct(
            &projection, &self.xBasisProjection, &self.normal)

        if signIndicator < 0: angle = 2 * M_PI - angle
        cdef float factor = angle / (2 * M_PI) - self.phase
        return factor - floor(factor)

# Assume the plane pass by the global origin and assume unit normal.
cdef void projectPointOnOriginPlane(Vector3 *normal, Vector3 *point,
        Vector3 *projection):
    cdef double distance
    cdef Vector3 projectionVector
    distance = dotVec3(point, normal)
    scaleVec3(&projectionVector, normal, -distance)
    addVec3(projection, point, &projectionVector)
