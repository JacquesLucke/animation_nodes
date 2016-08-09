from libc.math cimport floor
from ... math.ctypes cimport Vector3
from ... math.base_operations cimport mixVec3
from ... math.list_operations cimport transformVector3DList
from mathutils import Vector

# Great free online book about bezier curves:
# http://pomax.github.io/bezierinfo/

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
            float t1
            Vector3* w[4]
            long indices[2]
        self.calcPointIndicesAndMixFactor(t, indices, &t1)
        w[0] = (<Vector3*>self.points.base.data) + indices[0]
        w[1] = (<Vector3*>self.rightHandles.base.data) + indices[0]
        w[2] = (<Vector3*>self.leftHandles.base.data) + indices[1]
        w[3] = (<Vector3*>self.points.base.data) + indices[1]

        cdef:
            float t2 = t1 * t1
            float t3 = t2 * t1
            float mt1 = 1 - t1
            float mt2 = mt1 * mt1
            float mt3 = mt2 * mt1
            float coeff1 = 3 * mt2 * t1
            float coeff2 = 3 * mt1 * t2
        result.x = w[0].x*mt3 + w[1].x*coeff1 + w[2].x*coeff2 + w[3].x*t3
        result.y = w[0].y*mt3 + w[1].y*coeff1 + w[2].y*coeff2 + w[3].y*t3
        result.z = w[0].z*mt3 + w[1].z*coeff1 + w[2].z*coeff2 + w[3].z*t3

    cdef void evaluateTangent_LowLevel(self, float t, Vector3* result):
        cdef:
            float t1
            Vector3* w[4]
            long indices[2]
        self.calcPointIndicesAndMixFactor(t, indices, &t1)
        w[0] = (<Vector3*>self.points.base.data) + indices[0]
        w[1] = (<Vector3*>self.rightHandles.base.data) + indices[0]
        w[2] = (<Vector3*>self.leftHandles.base.data) + indices[1]
        w[3] = (<Vector3*>self.points.base.data) + indices[1]

        cdef:
            float t2 = t1 * t1
            float coeff0 = -3 +  6 * t1 - 3 * t2
            float coeff1 =  3 - 12 * t1 + 9 * t2
            float coeff2 =       6 * t1 - 9 * t2
            float coeff3 =                3 * t2
        result.x = w[0].x*coeff0 + w[1].x*coeff1 + w[2].x*coeff2 + w[3].x*coeff3
        result.y = w[0].y*coeff0 + w[1].y*coeff1 + w[2].y*coeff2 + w[3].y*coeff3
        result.z = w[0].z*coeff0 + w[1].z*coeff1 + w[2].z*coeff2 + w[3].z*coeff3

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
