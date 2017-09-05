cimport cython
from libc.math cimport floor
from libc.string cimport memcpy
from . base_spline import calculateNormalsForTangents
from ... utils.lists cimport findListSegment_LowLevel

from ... math cimport (
    Vector3, mixVec3, distanceVec3, subVec3,
    distanceSquaredVec3, findNearestLineParameter,
    distanceSumOfVector3DList
)

cdef class PolySpline(Spline):

    def __cinit__(self, Vector3DList points = None, FloatList radii = None, FloatList tilts = None, bint cyclic = False):
        if points is None:
            points = Vector3DList()
        if radii is None:
            radii = FloatList.fromValue(0.1, length = points.length)
        if tilts is None:
            tilts = FloatList.fromValue(0, length = points.length)
        if not (points.length == radii.length == tilts.length):
            raise Exception("Point and radius amount has to be equal")

        self.type = "POLY"
        self.points = points
        self.radii = radii
        self.tilts = tilts
        self.cyclic = cyclic
        self.markChanged()

    cpdef void markChanged(self):
        Spline.markChanged(self)
        self.normalsCache = None

    cpdef bint isEvaluable(self):
        return self.points.length >= 2

    def appendPoint(self, point, float radius = 0, float tilt = 0):
        self.points.append(point)
        self.radii.append(radius)
        self.tilts.append(tilt)
        self.markChanged()

    def copy(self):
        return PolySpline(self.points.copy(), self.radii.copy(), self.tilts.copy(), self.cyclic)

    def transform(self, matrix):
        self.points.transform(matrix)
        self.markChanged()

    def getLength(self, int resolution = 0):
        cdef double length = distanceSumOfVector3DList(self.points)
        if self.cyclic and self.points.length >= 2:
            length += distanceVec3(self.points.data + 0,
                                   self.points.data + self.points.length - 1)
        return length

    # Normals
    #################################################

    cdef checkNormals(self):
        if self.normalsCache is None:
            raise Exception("normals are not available yet, please call spline.ensureNormals() first")

    cpdef ensureNormals(self):
        if self.normalsCache is not None:
            return
        if not self.isEvaluable():
            raise Exception("cannot ensure normals when spline is not evaluable")

        cdef Py_ssize_t segments = getSegmentAmount(self)
        cdef Vector3DList tangents = Vector3DList(length = segments)
        cdef Py_ssize_t i
        cdef Vector3 start, end
        for i in range(segments):
            start = self.points.data[i]
            end = self.points.data[(i + 1) % self.points.length]
            subVec3(tangents.data + i, &end, &start)

        self.normalsCache = calculateNormalsForTangents(tangents, self.cyclic)

    cdef void evaluateNormal_Approximated(self, float parameter, Vector3 *result):
        cdef Py_ssize_t index = getSegmentIndex(self, parameter)
        result[0] = self.normalsCache.data[index]

    cdef float evaluateTilt_LowLevel(self, float parameter):
        cdef long indices[2]
        cdef float t
        findListSegment_LowLevel(self.tilts.length, self.cyclic, parameter, indices, &t)
        return self.tilts.data[indices[0]] * (1 - t) + self.tilts.data[indices[1]] * t

    # Projection
    #################################################

    @cython.cdivision(True)
    cdef float project_LowLevel(self, Vector3* point):
        cdef:
            float closestParameter = 0
            float smallestDistance = 1e9
            float lineParameter, lineDistance
            int segmentAmount = getSegmentAmount(self)
            int i, pointAmount = self.points.length
            Vector3 lineDirection, projectionOnLine
            Vector3 *_points = self.points.data
            int endIndex

        for i in range(segmentAmount):
            endIndex = (i + 1) % pointAmount

            # find closest t value on current segment
            subVec3(&lineDirection, _points + endIndex, _points + i)
            lineParameter = findNearestLineParameter(_points + i, &lineDirection, point)
            lineParameter = min(max(lineParameter, 0.0), 1.0)

            # calculate closest point on the current segment
            mixVec3(&projectionOnLine, _points + i, _points + endIndex, lineParameter)

            # check if it is closer than all previously calculated points
            lineDistance = distanceSquaredVec3(point, &projectionOnLine)
            if lineDistance < smallestDistance:
                smallestDistance = lineDistance
                closestParameter = (lineParameter + i) / <float>segmentAmount

        return closestParameter

    cdef PolySpline getTrimmedCopy_LowLevel(self, float start, float end):
        cdef:
            long startIndices[2]
            long endIndices[2]
            float startT, endT

        findListSegment_LowLevel(self.points.length, self.cyclic, start, startIndices, &startT)
        findListSegment_LowLevel(self.points.length, self.cyclic, end, endIndices, &endT)

        cdef long newPointAmount
        if endIndices[1] > 0:
            newPointAmount = endIndices[1] - startIndices[0] + 1
        elif endIndices[1] == 0: # <- cyclic extension required
            newPointAmount = self.points.length - startIndices[0] + 1

        cdef:
            Vector3DList newPoints = Vector3DList(length = newPointAmount)
            Vector3 *_newPoints = newPoints.data
            Vector3 *_oldPoints = self.points.data

            FloatList newRadii = FloatList(length = newPointAmount)
            float *_newRadii = newRadii.data
            float *_oldRadii = self.radii.data

            FloatList newTilts = FloatList(length = newPointAmount)
            float *_newTilts = newTilts.data
            float *_oldTilts = self.tilts.data

        # First Point
        mixVec3(_newPoints, _oldPoints + startIndices[0], _oldPoints + startIndices[1], startT)
        _newRadii[0] = _oldRadii[startIndices[0]] * (1 - startT) + _oldRadii[startIndices[1]] * startT
        _newTilts[0] = _oldTilts[startIndices[0]] * (1 - startT) + _oldTilts[startIndices[1]] * startT

        # Last Point
        mixVec3(_newPoints + newPointAmount - 1, _oldPoints + endIndices[0], _oldPoints + endIndices[1], endT)
        _newRadii[newPointAmount - 1] = _oldRadii[endIndices[0]] * (1 - endT) + _oldRadii[endIndices[1]] * endT
        _newTilts[newPointAmount - 1] = _oldTilts[endIndices[0]] * (1 - endT) + _oldTilts[endIndices[1]] * endT

        # In between
        memcpy(_newPoints + 1, _oldPoints + startIndices[1], sizeof(Vector3) * (newPointAmount - 2))
        memcpy(_newRadii + 1, _oldRadii + startIndices[1], sizeof(float) * (newPointAmount - 2))
        memcpy(_newTilts + 1, _oldTilts + startIndices[1], sizeof(float) * (newPointAmount - 2))

        return PolySpline(newPoints, newRadii, newTilts)


    cdef void evaluatePoint_LowLevel(self, float parameter, Vector3 *result):
        cdef:
            Vector3 *_points = self.points.data
            long indices[2]
            float t
        findListSegment_LowLevel(self.points.length, self.cyclic, parameter, indices, &t)
        mixVec3(result, _points + indices[0], _points + indices[1], t)

    cdef void evaluateTangent_LowLevel(self, float parameter, Vector3 *result):
        cdef:
            Vector3 *_points = self.points.data
            long indices[2]
            float t # not really needed here
        findListSegment_LowLevel(self.points.length, self.cyclic, parameter, indices, &t)
        subVec3(result, _points + indices[1], _points + indices[0])

    cdef float evaluateRadius_LowLevel(self, float parameter):
        cdef long indices[2]
        cdef float t
        findListSegment_LowLevel(self.points.length, self.cyclic, parameter, indices, &t)
        return self.radii.data[indices[0]] * (1 - t) + self.radii.data[indices[1]] * t

    @cython.cdivision(True)
    def getUniformParameters(self, Py_ssize_t amount):
        cdef:
            Py_ssize_t i
            Vector3* _points = self.points.data
            Py_ssize_t pointAmount = self.points.length

        if amount <= 1 or pointAmount <= 1:
            return FloatList.fromValue(0, length = amount)

        cdef FloatList distances = FloatList(length = pointAmount - 1 + int(self.cyclic))
        for i in range(pointAmount - 1):
            distances.data[i] = distanceVec3(_points + i, _points + i + 1)
        if self.cyclic:
            distances.data[pointAmount - 1] = distanceVec3(_points + pointAmount - 1, _points)

        cdef float totalLength = distances.getSumOfElements()
        if totalLength < 0.001: # <- necessary to remove the risk of running
                                #    into endless loops or division by 0
            return FloatList.fromValue(0, length = amount)

        cdef:
            # Safe Division: amount > 1
            float stepSize = totalLength / (amount - 1)
            float factor = 1 / <float>distances.length
            float missingDistance = stepSize
            float residualDistance
            Py_ssize_t currentIndex = 1
            FloatList parameters = FloatList(length = max(0, amount))

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

        return parameters


cdef inline int getSegmentAmount(PolySpline spline):
    return spline.points.length - 1 + spline.cyclic

cdef inline Py_ssize_t getSegmentIndex(PolySpline spline, float parameter):
    cdef long indices[2]
    cdef float t
    findListSegment_LowLevel(spline.points.length, spline.cyclic, parameter, indices, &t)
    return indices[0]
