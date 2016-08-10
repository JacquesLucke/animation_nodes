from libc.math cimport floor
from . utils cimport calcSegmentIndicesAndFactor
from ... math.ctypes cimport Vector3
from ... math.base_operations cimport mixVec3, distanceVec3, subVec3
from ... math.list_operations cimport (
                                transformVector3DList,
                                distanceSumOfVector3DList)

from mathutils import Vector

cdef class PolySpline(Spline):

    def __cinit__(self, Vector3DList points = None):
        if points is None: points = Vector3DList()
        self.cyclic = False
        self.type = "POLY"
        self.points = points

    def appendPoint(self, point):
        self.points.append(point)

    cpdef PolySpline copy(self):
        cdef PolySpline newSpline = PolySpline()
        newSpline.cyclic = self.cyclic
        newSpline.points = self.points.copy()
        return newSpline

    cpdef transform(self, matrix):
        transformVector3DList(self.points, matrix)

    cpdef double getLength(self, resolution = 0):
        cdef double length = distanceSumOfVector3DList(self.points)
        cdef Vector3* _points
        if self.cyclic and self.points.getLength() >= 2:
            _points = <Vector3*>self.points.base.data
            length += distanceVec3(_points + 0, _points + self.points.getLength() - 1)
        return length

    cpdef bint isEvaluable(self):
        return self.points.getLength() >= 2

    cdef void evaluate_LowLevel(self, float parameter, Vector3* result):
        cdef:
            Vector3* _points = <Vector3*>self.points.base.data
            long indices[2]
            float t
        calcSegmentIndicesAndFactor(self.points.getLength(), self.cyclic, parameter, indices, &t)
        mixVec3(result, _points + indices[0], _points + indices[1], t)

    cdef void evaluateTangent_LowLevel(self, float parameter, Vector3* result):
        cdef:
            Vector3* _points = <Vector3*>self.points.base.data
            long indices[2]
            float t # not really needed here
        calcSegmentIndicesAndFactor(self.points.getLength(), self.cyclic, parameter, indices, &t)
        subVec3(result, _points + indices[1], _points + indices[0])
