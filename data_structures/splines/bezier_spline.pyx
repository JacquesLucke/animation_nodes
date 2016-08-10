cimport cython
from . utils cimport calcSegmentIndicesAndFactor
from ... math.list_operations cimport transformVector3DList
from ... math.base_operations cimport addVec3, mixVec3, subVec3, normalizeVec3, lengthVec3, scaleVec3
from mathutils import Vector

# Great free online book about bezier curves:
# http://pomax.github.io/bezierinfo/

cdef class BezierSpline(Spline):

    def __cinit__(self, Vector3DList points = None,
                        Vector3DList leftHandles = None,
                        Vector3DList rightHandles = None):
        if points is None: points = Vector3DList()
        if leftHandles is None: leftHandles = Vector3DList()
        if rightHandles is None: rightHandles = Vector3DList()

        if not (points.getLength() == leftHandles.getLength() == points.getLength()):
            raise ValueError("list lengths have to be equal")

        self.points = points
        self.leftHandles = leftHandles
        self.rightHandles = rightHandles
        self.type = "BEZIER"

    cpdef appendPoint(self, point, leftHandle, rightHandle):
        self.points.append(point)
        self.leftHandles.append(leftHandle)
        self.rightHandles.append(rightHandle)

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

    cdef void evaluate_LowLevel(self, float parameter, Vector3* result):
        cdef:
            float t1
            Vector3* w[4]
        self.getSegmentData(parameter, &t1, w)
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

    cdef void evaluateTangent_LowLevel(self, float parameter, Vector3* result):
        cdef:
            float t1
            Vector3* w[4]
        self.getSegmentData(parameter, &t1, w)
        cdef:
            float t2 = t1 * t1
            float coeff0 = -3 +  6 * t1 - 3 * t2
            float coeff1 =  3 - 12 * t1 + 9 * t2
            float coeff2 =       6 * t1 - 9 * t2
            float coeff3 =                3 * t2
        result.x = w[0].x*coeff0 + w[1].x*coeff1 + w[2].x*coeff2 + w[3].x*coeff3
        result.y = w[0].y*coeff0 + w[1].y*coeff1 + w[2].y*coeff2 + w[3].y*coeff3
        result.z = w[0].z*coeff0 + w[1].z*coeff1 + w[2].z*coeff2 + w[3].z*coeff3

    cdef void getSegmentData(self, float parameter, float* t, Vector3** w):
        cdef long indices[2]
        calcSegmentIndicesAndFactor(self.points.getLength(), self.cyclic, parameter, indices, t)
        w[0] = (<Vector3*>self.points.base.data) + indices[0]
        w[1] = (<Vector3*>self.rightHandles.base.data) + indices[0]
        w[2] = (<Vector3*>self.leftHandles.base.data) + indices[1]
        w[3] = (<Vector3*>self.points.base.data) + indices[1]

    @cython.cdivision(True)
    cpdef calculateSmoothHandles(self, float strength = 1/3):
        cdef:
            Vector3* _points = <Vector3*>self.points.base.data
            Vector3* _leftHandles = <Vector3*>self.leftHandles.base.data
            Vector3* _rightHandles = <Vector3*>self.rightHandles.base.data
            long indexLeft, i, indexRight
            long pointAmount = self.points.getLength()

        if pointAmount < 2: return

        for i in range(1, pointAmount - 1):
            calculateSmoothControlPoints(
                _points + i, _points + i - 1, _points + i + 1, strength,
                _leftHandles + i, _rightHandles + i)

        # End points need extra consideration
        cdef long lastIndex = pointAmount - 1
        if self.cyclic:
            # Start Point
            calculateSmoothControlPoints(
                _points, _points + lastIndex, _points + 1, strength,
                _leftHandles, _rightHandles)
            # End Point
            calculateSmoothControlPoints(
                _points + lastIndex, _points + lastIndex - 1, _points, strength,
                _leftHandles + lastIndex, _rightHandles + lastIndex)
        else:
            # Start Point
            _leftHandles[0] = _points[0]
            _rightHandles[0] = _points[0]
            # End Point
            _leftHandles[lastIndex] = _points[lastIndex]
            _rightHandles[lastIndex] = _points[lastIndex]

cdef calculateSmoothControlPoints(
                Vector3* point, Vector3* left, Vector3* right, float strength,
                Vector3* leftHandle, Vector3* rightHandle):   # <- output
    # http://stackoverflow.com/questions/13037606/how-does-inkscape-calculate-the-coordinates-for-control-points-for-smooth-edges/13425159#13425159
    cdef:
        Vector3 vecLeft, vecRight
        double lenLeft, lenRight
        Vector3 direction, directionLeft, directionRight

    subVec3(&vecLeft, left, point)
    subVec3(&vecRight, right, point)
    lenLeft = lengthVec3(&vecLeft)
    lenRight = lengthVec3(&vecRight)

    if lenLeft > 0 and lenRight > 0:
        # TODO: Inline manually (check if it matters)
        scaleVec3(&vecRight, factor = lenLeft / lenRight)
        subVec3(&direction, &vecRight, &vecLeft)
        normalizeVec3(&direction)

        directionLeft = direction
        directionRight = direction

        scaleVec3(&directionLeft, -lenLeft * strength)
        scaleVec3(&directionRight, lenRight * strength)

        addVec3(leftHandle, point, &directionLeft)
        addVec3(rightHandle, point, &directionRight)
