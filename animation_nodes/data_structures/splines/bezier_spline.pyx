cimport cython
from libc.string cimport memcpy
from numpy.polynomial import Polynomial
from ... utils.lists cimport findListSegment_LowLevel
from ... math cimport (
    subVec3, normalizeVec3_InPlace, lengthVec3,
    toPyVector3, mixVec3, isCloseVec3
)

from mathutils import Vector
from . base_spline import calculateNormalsForTangents

cdef Py_ssize_t normalsResolution = 5

# Great free online book about bezier curves:
# http://pomax.github.io/bezierinfo/

cdef class BezierSpline(Spline):

    def __cinit__(self, Vector3DList points = None,
                        Vector3DList leftHandles = None,
                        Vector3DList rightHandles = None,
                        FloatList radii = None,
                        FloatList tilts = None,
                        bint cyclic = False):
        if points is None: points = Vector3DList()
        if leftHandles is None: leftHandles = points.copy()
        if rightHandles is None: rightHandles = points.copy()
        if radii is None: radii = FloatList.fromValue(0.1, length = points.length)
        if tilts is None: tilts = FloatList.fromValue(0, length = points.length)

        if not (points.length == leftHandles.length == points.length == radii.length == tilts.length):
            raise ValueError("list lengths have to be equal")

        self.points = points
        self.leftHandles = leftHandles
        self.rightHandles = rightHandles
        self.radii = radii
        self.tilts = tilts
        self.cyclic = cyclic
        self.type = "BEZIER"
        self.markChanged()

    cpdef void markChanged(self):
        Spline.markChanged(self)
        self.normalsCache = None

    cpdef bint isEvaluable(self):
        return self.points.length >= 2

    def appendPoint(self, point, leftHandle, rightHandle, float radius = 0, float tilt = 0):
        self.points.append(point)
        self.leftHandles.append(leftHandle)
        self.rightHandles.append(rightHandle)
        self.radii.append(radius)
        self.tilts.append(tilt)
        self.markChanged()

    def copy(self):
        return BezierSpline(self.points.copy(),
                            self.leftHandles.copy(),
                            self.rightHandles.copy(),
                            self.radii.copy(),
                            self.tilts.copy(),
                            self.cyclic)

    def transform(self, matrix):
        self.points.transform(matrix)
        self.leftHandles.transform(matrix)
        self.rightHandles.transform(matrix)
        self.markChanged()

    # Normals
    ############################################################

    cdef checkNormals(self):
        if self.normalsCache is None:
            raise Exception("normals are not available yet, please call spline.ensureNormals() first")

    cpdef ensureNormals(self):
        if self.normalsCache is not None:
            return
        if not self.isEvaluable():
            raise Exception("cannot ensure normals when spline is not evaluable")

        cdef Py_ssize_t segments = getSegmentAmount(self)
        cdef Py_ssize_t amount = segments * normalsResolution
        cdef Vector3DList tangents = Vector3DList(length = amount)

        cdef Py_ssize_t segment, i
        cdef Py_ssize_t index = 0
        cdef Vector3* w[4]
        cdef float t
        for segment in range(segments):
            getSegmentData_Index(self, segment, w)
            for i in range(normalsResolution):
                t = i / <float>(normalsResolution - 1)
                evaluateBezierSegment_Tangent(tangents.data + index, t, w)
                index += 1

        self.normalsCache = calculateNormalsForTangents(tangents, self.cyclic)

    cdef void evaluateNormal_Approximated(self, float parameter, Vector3 *result):
        cdef float t
        cdef Py_ssize_t segment
        getSegmentIndex(self, parameter, &segment, &t)

        cdef long indices[2]
        cdef float f
        findListSegment_LowLevel(normalsResolution, False, t, indices, &f)

        cdef Py_ssize_t offset = segment * normalsResolution
        mixVec3(result,
            self.normalsCache.data + offset + indices[0],
            self.normalsCache.data + offset + indices[1],
            f)

    cdef float evaluateTilt_LowLevel(self, float parameter):
        cdef long indices[2]
        cdef float t
        findListSegment_LowLevel(self.tilts.length, self.cyclic, parameter, indices, &t)
        return self.tilts.data[indices[0]] * (1 - t) + self.tilts.data[indices[1]] * t

    # Projection
    ############################################################

    cdef float project_LowLevel(self, Vector3* _point):
        # TODO: Speedup using cython
        # slowest part here is the root finding using numpy
        # maybe implement another numerical method to find the best parameter
        # http://jazzros.blogspot.be/2011/03/projecting-point-on-bezier-curve.html
        cdef:
            int segmentAmount = getSegmentAmount(self)
            Py_ssize_t i
            Vector3 *w[4]
            set possibleParameters = set()
            list coeffs = [0] * 6

        point = toPyVector3(_point)

        for i in range(segmentAmount):
            getSegmentData_Index(self, i, w)
            p0 = toPyVector3(w[0]) - point
            p1 = toPyVector3(w[1]) - point
            p2 = toPyVector3(w[2]) - point
            p3 = toPyVector3(w[3]) - point

            a = p3 - 3 * p2 + 3 * p1 - p0
            b = 3 * p2 - 6 * p1 + 3 * p0
            c = 3 * (p1 - p0)

            coeffs[0] = c.dot(p0)
            coeffs[1] = c.dot(c) + b.dot(p0) * 2.0
            coeffs[2] = b.dot(c) * 3.0 + a.dot(p0) * 3.0
            coeffs[3] = a.dot(c) * 4.0 + b.dot(b) * 2.0
            coeffs[4] = a.dot(b) * 5.0
            coeffs[5] = a.dot(a) * 3.0

            poly = Polynomial(coeffs, [0.0, 1.0], [0.0, 1.0])
            roots = poly.roots()
            realRoots = [float(min(max(root.real, 0), 1)) for root in roots]
            segmentParameters = [(i + t) / segmentAmount for t in realRoots]
            possibleParameters.update(segmentParameters)

        sampledData = [(p, (point - self.evaluatePoint(p)).length_squared) for p in possibleParameters]
        if len(sampledData) > 0:
            return min(sampledData, key = lambda item: item[1])[0]
        return 0


    cdef void evaluatePoint_LowLevel(self, float parameter, Vector3 *result):
        cdef float t
        cdef Vector3* w[4]
        getSegmentData_Parameter(self, parameter, &t, w)
        evaluateBezierSegment_Point(result, t, w)

    cdef void evaluateTangent_LowLevel(self, float parameter, Vector3* result):
        cdef float t
        cdef Vector3* w[4]
        getSegmentData_Parameter(self, parameter, &t, w)
        evaluateBezierSegment_Tangent(result, t, w)

    cdef float evaluateRadius_LowLevel(self, float parameter):
        cdef long indices[2]
        cdef float t
        findListSegment_LowLevel(self.points.length, self.cyclic, parameter, indices, &t)
        return self.radii.data[indices[0]] * (1 - t) + self.radii.data[indices[1]] * t

    def smoothAllHandles(self, float strength = 1/3):
        cdef Py_ssize_t i
        for i in range(self.points.length):
            smoothPoint(self, i, strength)
        self.markChanged()

    def smoothHandle(self, Py_ssize_t index, float strength = 1/3):
        if not (0 <= index < self.points.length):
            raise IndexError("index is out of bounds")
        smoothPoint(self, index, strength)
        self.markChanged()

    cpdef BezierSpline getTrimmedCopy_LowLevel(self, float start, float end):
        cdef:
            long startIndices[2]
            long endIndices[2]
            float startT, endT

        findListSegment_LowLevel(self.points.length, self.cyclic, start, startIndices, &startT)
        findListSegment_LowLevel(self.points.length, self.cyclic, end, endIndices, &endT)

        cdef long newPointAmount
        if endIndices[1] == 0: # <- cyclic extension required
            newPointAmount = self.points.length - startIndices[0] + 1
        else:
            newPointAmount = endIndices[1] - startIndices[0] + 1

        cdef:
            Vector3DList newPoints = Vector3DList(length = newPointAmount)
            Vector3* _newPoints = newPoints.data
            Vector3* _oldPoints = self.points.data

            Vector3DList newLeftHandles = Vector3DList(length = newPointAmount)
            Vector3* _newLeftHandles = newLeftHandles.data
            Vector3* _oldLeftHandles = self.leftHandles.data

            Vector3DList newRightHandles = Vector3DList(length = newPointAmount)
            Vector3* _newRightHandles = newRightHandles.data
            Vector3* _oldRightHandles = self.rightHandles.data

            FloatList newRadii = FloatList(length = newPointAmount)
            float *_newRadii = newRadii.data
            float *_oldRadii = self.radii.data

            FloatList newTilts = FloatList(length = newPointAmount)
            float *_newTilts = newTilts.data
            float *_oldTilts = self.tilts.data

            Vector3 tmp[4]

        if startIndices[0] == endIndices[0]: # <- result will contain only one segment
            if endT < 0.0001: # <- both parameters are (nearly) zero, avoid division by zero
                _newPoints[0] = _oldPoints[startIndices[0]]
                _newPoints[1] = _oldPoints[startIndices[0]]
                _newLeftHandles[0] = _oldPoints[startIndices[0]]
                _newLeftHandles[1] = _oldPoints[startIndices[0]]
                _newRightHandles[0] = _oldPoints[startIndices[0]]
                _newRightHandles[1] = _oldPoints[startIndices[0]]
            else: # <- trim segment from both ends
                calcRightTrimmedSegment(endT,
                                   _oldPoints + startIndices[0], _oldRightHandles + startIndices[0],
                                   _oldLeftHandles + startIndices[1], _oldPoints + startIndices[1],
                                   tmp + 0, tmp + 1, tmp + 2, tmp + 3)
                calcLeftTrimmedSegment(startT / endT,
                                   tmp + 0, tmp + 1, tmp + 2, tmp + 3,
                                   _newPoints + 0, _newRightHandles + 0,
                                   _newLeftHandles + 1, _newPoints + 1)
                _newLeftHandles[0] = _newPoints[0]
                _newRightHandles[1] = _newPoints[1]
        else: # <- resulting spline will contain multiple segments
            # Copy segments which stay the same
            memcpy(_newPoints + 1,
                   _oldPoints + startIndices[1],
                   sizeof(Vector3) * (newPointAmount - 2))
            memcpy(_newLeftHandles + 1,
                   _oldLeftHandles + startIndices[1],
                   sizeof(Vector3) * (newPointAmount - 2))
            memcpy(_newRightHandles + 1,
                   _oldRightHandles + startIndices[1],
                   sizeof(Vector3) * (newPointAmount - 2))
            memcpy(_newRadii + 1,
                   _oldRadii + startIndices[1],
                   sizeof(float) * (newPointAmount - 2))
            memcpy(_newTilts + 1,
                   _oldTilts + startIndices[1],
                   sizeof(float) * (newPointAmount - 2))

            # Trim first segment
            calcLeftTrimmedSegment(startT,
                _oldPoints + startIndices[0], _oldRightHandles + startIndices[0],
                _oldLeftHandles + startIndices[1], _oldPoints + startIndices[1],
                _newPoints, _newRightHandles,
                _newLeftHandles + 1, _newPoints + 1)
            _newLeftHandles[0] = _newPoints[0]

            # Trim last segment
            calcRightTrimmedSegment(endT,
                _oldPoints + endIndices[0], _oldRightHandles + endIndices[0],
                _oldLeftHandles + endIndices[1], _oldPoints + endIndices[1],
                _newPoints + newPointAmount - 2, _newRightHandles + newPointAmount - 2,
                _newLeftHandles + newPointAmount - 1, _newPoints + newPointAmount - 1)
            _newRightHandles[newPointAmount - 1] = _newPoints[newPointAmount - 1]

        # calculate radius of first and last point
        _newRadii[0] = _oldRadii[startIndices[0]] * (1 - startT) + _oldRadii[startIndices[1]] * startT
        _newRadii[newPointAmount - 1] = _oldRadii[endIndices[0]] * (1 - endT) + _oldRadii[endIndices[1]] * endT

        # calculate tilt of first and last point
        _newTilts[0] = _oldTilts[startIndices[0]] * (1 - startT) + _oldTilts[startIndices[1]] * startT
        _newTilts[newPointAmount - 1] = _oldTilts[endIndices[0]] * (1 - endT) + _oldTilts[endIndices[1]] * endT

        return BezierSpline(newPoints, newLeftHandles, newRightHandles, newRadii, newTilts)

    def improveStraightBezierSegments(self):
        cdef Py_ssize_t i
        cdef Vector3* w[4]
        for i in range(getSegmentAmount(self)):
            getSegmentData_Index(self, i, w)
            if isCloseVec3(w[0], w[1]) and isCloseVec3(w[2], w[3]):
                mixVec3(w[1], w[0], w[3], 1.0 / 3.0)
                mixVec3(w[2], w[0], w[3], 2.0 / 3.0)

cdef smoothPoint(BezierSpline spline, Py_ssize_t index, float strength):
    if 0 < index < spline.points.length - 1:
        calculateSmoothControlPoints(spline.points.data + index,
            spline.points.data + index - 1, spline.points.data + index + 1,
            strength,
            spline.leftHandles.data + index, spline.rightHandles.data + index)
        return

    cdef Py_ssize_t lastIndex = spline.points.length - 1

    if index == 0:
        if spline.cyclic:
            calculateSmoothControlPoints(spline.points.data + 0,
                spline.points.data + lastIndex, spline.points.data + 1,
                strength,
                spline.leftHandles.data + 0, spline.rightHandles.data + 0)
            return
        else:
            mixVec3(spline.leftHandles.data + 0,
                    spline.points.data + 0,
                    spline.points.data + 1,
                    -strength)
            mixVec3(spline.rightHandles.data + 0,
                    spline.points.data + 0,
                    spline.points.data + 1,
                    strength)
            return

    if index == lastIndex:
        if spline.cyclic:
            calculateSmoothControlPoints(spline.points.data + lastIndex,
                spline.points.data + lastIndex - 1, spline.points.data + 0,
                strength,
                spline.leftHandles.data + lastIndex, spline.rightHandles.data + lastIndex)
            return
        else:
            mixVec3(spline.leftHandles.data + lastIndex,
                    spline.points.data + lastIndex,
                    spline.points.data + lastIndex - 1,
                    strength)
            mixVec3(spline.rightHandles.data + lastIndex,
                    spline.points.data + lastIndex,
                    spline.points.data + lastIndex - 1,
                    -strength)
            return

@cython.cdivision(True)
cdef calculateSmoothControlPoints(
                Vector3* point, Vector3* left, Vector3* right, float strength,
                Vector3* leftHandle, Vector3* rightHandle):   # <- output
    # http://stackoverflow.com/questions/13037606/how-does-inkscape-calculate-the-coordinates-for-control-points-for-smooth-edges/13425159#13425159
    cdef:
        Vector3 vecLeft, vecRight
        float lenLeft, lenRight, factor
        Vector3 direction, directionLeft, directionRight

    subVec3(&vecLeft, left, point)
    subVec3(&vecRight, right, point)
    lenLeft = lengthVec3(&vecLeft)
    lenRight = lengthVec3(&vecRight)

    if lenLeft > 0 and lenRight > 0:
        factor = lenLeft / lenRight
        direction.x = factor * vecRight.x - vecLeft.x
        direction.y = factor * vecRight.y - vecLeft.y
        direction.z = factor * vecRight.z - vecLeft.z
        normalizeVec3_InPlace(&direction)

        factor = lenLeft * strength
        leftHandle.x = point.x - direction.x * factor
        leftHandle.y = point.y - direction.y * factor
        leftHandle.z = point.z - direction.z * factor

        factor = lenRight * strength
        rightHandle.x = point.x + direction.x * factor
        rightHandle.y = point.y + direction.y * factor
        rightHandle.z = point.z + direction.z * factor
    else:
        leftHandle[0] = point[0]
        rightHandle[0] = point[0]

cdef calcLeftTrimmedSegment(float t,
                    Vector3* P1, Vector3* P2, Vector3* P3, Vector3* P4,
                    Vector3* outP1, Vector3* outP2, Vector3* outP3, Vector3* outP4):
    calcRightTrimmedSegment(1 - t, P4, P3, P2, P1, outP4, outP3, outP2, outP1)

cdef calcRightTrimmedSegment(float t,
                    Vector3* P1, Vector3* P2, Vector3* P3, Vector3* P4,
                    Vector3* outP1, Vector3* outP2, Vector3* outP3, Vector3* outP4):
    '''
    t: how much of the curve will stay (0-1)
    P1: left point
    P2: right handle of left point
    P3: left handle of right point
    P4: right point
    outPX: new location of that point
    '''
    cdef float t2 = t * t
    cdef float t3 = t2 * t

    outP1[0] = P1[0]

    outP2.x = t * P2.x - (t-1) * P1.x
    outP2.y = t * P2.y - (t-1) * P1.y
    outP2.z = t * P2.z - (t-1) * P1.z

    outP3.x = t2 * P3.x - 2 * t * (t-1) * P2.x + (t-1) ** 2 * P1.x
    outP3.y = t2 * P3.y - 2 * t * (t-1) * P2.y + (t-1) ** 2 * P1.y
    outP3.z = t2 * P3.z - 2 * t * (t-1) * P2.z + (t-1) ** 2 * P1.z

    outP4.x = t3 * P4.x - 3 * t2 * (t-1) * P3.x + 3 * t * (t-1) ** 2 * P2.x - (t-1) ** 3 * P1.x
    outP4.y = t3 * P4.y - 3 * t2 * (t-1) * P3.y + 3 * t * (t-1) ** 2 * P2.y - (t-1) ** 3 * P1.y
    outP4.z = t3 * P4.z - 3 * t2 * (t-1) * P3.z + 3 * t * (t-1) ** 2 * P2.z - (t-1) ** 3 * P1.z


cdef inline void getSegmentData_Parameter(BezierSpline spline, float parameter,
                                          float *t, Vector3 **w):
    cdef long indices[2]
    findListSegment_LowLevel(spline.points.length, spline.cyclic, parameter, indices, t)
    w[0] = spline.points.data + indices[0]
    w[1] = spline.rightHandles.data + indices[0]
    w[2] = spline.leftHandles.data + indices[1]
    w[3] = spline.points.data + indices[1]

cdef inline void getSegmentData_Index(BezierSpline spline, Py_ssize_t index, Vector3 **w):
    cdef Py_ssize_t i1 = index
    cdef Py_ssize_t i2 = index + 1
    if i2 == spline.points.length:
        i2 = 0

    w[0] = spline.points.data + i1
    w[1] = spline.rightHandles.data + i1
    w[2] = spline.leftHandles.data + i2
    w[3] = spline.points.data + i2

cdef inline void getSegmentIndex(BezierSpline spline, float parameter, Py_ssize_t *index, float *t):
    cdef long indices[2]
    findListSegment_LowLevel(spline.points.length, spline.cyclic, parameter, indices, t)
    index[0] = indices[0]

cdef inline int getSegmentAmount(BezierSpline spline):
    return spline.points.length - 1 + spline.cyclic

cdef inline void evaluateBezierSegment_Point(Vector3 *result, float t, Vector3 **w):
    cdef:
        float t2 = t * t
        float t3 = t2 * t
        float mt1 = 1 - t
        float mt2 = mt1 * mt1
        float mt3 = mt2 * mt1
        float coeff1 = 3 * mt2 * t
        float coeff2 = 3 * mt1 * t2
    result.x = w[0].x*mt3 + w[1].x*coeff1 + w[2].x*coeff2 + w[3].x*t3
    result.y = w[0].y*mt3 + w[1].y*coeff1 + w[2].y*coeff2 + w[3].y*t3
    result.z = w[0].z*mt3 + w[1].z*coeff1 + w[2].z*coeff2 + w[3].z*t3

cdef inline void evaluateBezierSegment_Tangent(Vector3 *result, float t, Vector3 **w):
    cdef:
        float t2 = t * t
        float coeff0 = -3 +  6 * t - 3 * t2
        float coeff1 =  3 - 12 * t + 9 * t2
        float coeff2 =       6 * t - 9 * t2
        float coeff3 =                3 * t2
    result.x = w[0].x*coeff0 + w[1].x*coeff1 + w[2].x*coeff2 + w[3].x*coeff3
    result.y = w[0].y*coeff0 + w[1].y*coeff1 + w[2].y*coeff2 + w[3].y*coeff3
    result.z = w[0].z*coeff0 + w[1].z*coeff1 + w[2].z*coeff2 + w[3].z*coeff3
