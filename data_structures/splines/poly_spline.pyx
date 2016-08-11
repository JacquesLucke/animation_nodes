cimport cython
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

    @cython.cdivision(True)
    cpdef FloatList getUniformParameters(self, long amount):
        cdef:
            long i
            FloatList parameters = FloatList(length = max(0, amount))
            Vector3* _points = <Vector3*>self.points.base.data
            long pointAmount = self.points.getLength()

        if amount <= 1 or pointAmount <= 1:
            parameters.fill(0)
            return parameters

        cdef FloatList distances = FloatList(length = pointAmount - 1 + int(self.cyclic))
        for i in range(pointAmount - 1):
            distances.data[i] = distanceVec3(_points + i, _points + i + 1)
        if self.cyclic:
            distances.data[pointAmount - 1] = distanceVec3(_points + pointAmount - 1, _points)

        cdef float totalLength = distances.getSumOfElements()
        if totalLength < 0.001: # <- necessary to remove the risk of running
            parameters.fill(0)  #    into endless loops or division by 0
            return parameters

        cdef:
            # Safe Division: amount > 1
            float stepSize = totalLength / (amount - 1)
            float factor = 1 / <float>distances.length
            float missingDistance = stepSize
            float residualDistance
            long currentIndex = 1

        for i in range(distances.length):
            residualDistance = distances.data[i]
            while residualDistance > missingDistance and currentIndex < amount:
                residualDistance -= missingDistance
                # Safe Division: distances.data[i] > 0
                parameters.data[currentIndex] = (i + 1 - residualDistance / distances.data[i]) * factor
                missingDistance = stepSize
                currentIndex += 1
            missingDistance -= residualDistance

        parameters.data[0] = 0
        # It can happen that more than one element is 1 due to float inaccuracy
        for i in range(currentIndex, amount):
            parameters.data[i] = 1
        parameters.data[amount - 1]
        return parameters
