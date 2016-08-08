from libc.math cimport floor
from .. math.ctypes cimport Vector3
from .. math.base_operations cimport mixVec3
from .. math.list_operations cimport (
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

    def getPoints(self):
        return self.points

    cpdef PolySpline copy(self):
        cdef PolySpline newSpline = PolySpline()
        newSpline.cyclic = self.cyclic
        newSpline.points = self.pointy.copy()
        return newSpline

    cpdef transform(self, matrix):
        transformVector3DList(self.points, matrix)

    cpdef double getLength(self, resolution = 0):
        return distanceSumOfVector3DList(self.points)

    cpdef void update(self):
        pass

    cpdef bint isEvaluable(self):
        return self.points.getLength() >= 2

    cpdef evaluate(self, float t):
        if t < 0 or t > 1:
            raise ValueError("parameter has to be between 0 and 1")
        if not self.isEvaluable():
            raise Exception("spline is not evaluable")
        cdef Vector3 result
        self.evaluate_LowLevel(t, &result)
        return Vector((result.x, result.y, result.z))

    cdef void evaluate_LowLevel(self, float t, Vector3* result):
        cdef:
            Vector3* _points = <Vector3*>self.points.base.data
            long indices[2]
            float factor
        self.calcPointIndicesAndMixFactor(t, indices, &factor)
        mixVec3(result, _points + indices[0], _points + indices[1], factor)

    cdef void calcPointIndicesAndMixFactor(self, float t, long* index, float* factor):
        cdef long pointAmount = self.points.getLength()
        if not self.cyclic:
            if t < 1:
                index[0] = <long>floor(t * (pointAmount - 1))
                index[1] = index[0] + 1
                factor[0] = t * (pointAmount - 1) - index[0]
            else:
                index[0] = pointAmount - 1
                index[1] = index[0]
                factor[0] = 1
        else:
            # TODO
            index[0] = 0
            index[1] = 0
            factor[0]= 0
