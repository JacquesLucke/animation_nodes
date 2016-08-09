from libc.math cimport floor
from ... math.ctypes cimport Vector3
from ... math.base_operations cimport mixVec3
from ... math.list_operations cimport transformVector3DList

cdef class BezierSpline(Spline):

    def __cinit__(self, Vector3DList points,
                        Vector3DList leftHandles,
                        Vector3DList rightHandles):
        if points is None: points = Vector3DList()
        if leftHandles is None: leftHandles = Vector3DList()
        if rightHandles is None: rightHandles = Vector3DList()

        if not (points.getLength() == leftHandles.getLength() == points.getLength()):
            raise ValueError("list lengths have to be equal")

        self.points = points
        self.leftHandles = leftHandles
        self.rightHandles = rightHandles
        self.type = "BEZIER"

    cpdef BezierSpline copy(self):
        cdef BezierSpline newSpline = BezierSpline(
                self.points.copy(),
                self.leftHandles.copy(),
                self.rightHandles.copy())
        newSpline.cyclic = self.cyclic
        return newSpline

    cpdef transform(self, matrix):
        transformVector3DList(self.points, matrix)
        transformVector3DList(self.leftHandles, matrix)
        transformVector3DList(self.rightHandles, matrix)

    cpdef bint isEvaluable(self):
        return self.points.getLength() >= 2

    cdef void evaluate_LowLevel(self, float t, Vector3* result):
        cdef:
            long indices[2]
            float factor
            Vector3* start
            Vector3* startControl
            Vector3* endControl
            Vector3* end
        self.calcPointIndicesAndMixFactor(t, indices, &factor)
        start = (<Vector3*>self.points.base.data) + indices[0]
        end = (<Vector3*>self.points.base.data) + indices[1]
        startControl = (<Vector3*>self.rightHandles.base.data) + indices[0]
        endControl = (<Vector3*>self.leftHandles.base.data) + indices[1]
        mixVec3(result, start, end, factor)

    cdef void evaluateTangent_LowLevel(self, float t, Vector3* result):
        result.x = 0
        result.y = 0
        result.z = 0

    cdef void calcPointIndicesAndMixFactor(self, float t, long* index, float* factor):
        cdef long pointAmount = self.points.getLength()
        if not self.cyclic:
            if t < 1:
                index[0] = <long>floor(t * (pointAmount - 1))
                index[1] = index[0] + 1
                factor[0] = t * (pointAmount - 1) - index[0]
            else:
                index[0] = pointAmount - 2
                index[1] = pointAmount - 1
                factor[0] = 1
        else:
            if t < 1:
                index[0] = <long>floor(t * pointAmount)
                index[1] = index[0] + 1 if index[0] < (pointAmount - 1) else 0
                factor[0] = t * pointAmount - index[0]
            else:
                index[0] = pointAmount - 1
                index[1] = 0
                factor[0] = 1
