cimport cython
from libc.math cimport sin, cos, tan
from libc.math cimport M_PI as PI
from ... data_structures cimport (
    PolySpline, BezierSpline,
    VirtualDoubleList, Vector3DList, FloatList,
)
from ... math cimport (
    Vector3, subVec3, addVec3, scaleVec3,
    angleVec3Normalized, normalizeVec3_InPlace,
)

# Let A and B be two non parallel straight lines that intersect at P. A and B
# are tangent to a circle whose center is C and radius is r at D and E
# respectively. The corner DPE is the angle we want to bevel. We do that by
# splitting the point into two Bezier points that approximates the arc DE. The
# locations of those Bezier points should be D and E. Since PC bisects DPE and
# A and B are tangents, then the length of DP and PE are:
#
#     DP = PE = r / tan(theta / 2)
#
# where theta is the angle DPE. D and E can then be computed by means of vector
# math. The left and right handles of the Bezier points should also be tangent
# to the circle, meaning they should lie on A and B. The length of handles is
# computed through the equation described here:
#
#     https://pomax.github.io/bezierinfo/#circles_cubic
#
# Which is:
#
#     r * (4 / 3) * tan(beta / 4)
#
# Where beta is the arc angle DE. Since CDP and CEP are right angles. This
# angle is computed by complementing the quadrilateral DPEC as follows:
#
#     beta = pi - theta


@cython.cdivision(True)
cdef float computeTangentLength(double radius, float angle):
    return radius / tan(angle / 2) if angle != 0 else 0

@cython.cdivision(True)
cdef float computeHandleLength(double radius, float angle):
    return radius * (4.0 / 3.0) * tan((PI - angle) / 4)

cdef void bevelPart(Vector3 *left, Vector3 *center, Vector3 *right, double radius,
                    Vector3 *leftPoint, Vector3 *leftLeftHandle, Vector3 *leftRightHandle,
                    Vector3 *rightPoint, Vector3 *rightLeftHandle, Vector3 *rightRightHandle):
    cdef Vector3 leftDirection;
    subVec3(&leftDirection, left, center)
    normalizeVec3_InPlace(&leftDirection)

    cdef Vector3 rightDirection;
    subVec3(&rightDirection, right, center)
    normalizeVec3_InPlace(&rightDirection)

    cdef float angle = angleVec3Normalized(&leftDirection, &rightDirection)
    cdef float tangentLength = computeTangentLength(radius, angle)
    cdef float handleLength = computeHandleLength(radius, angle)

    cdef Vector3 directionToLeftPoint
    scaleVec3(&directionToLeftPoint, &leftDirection, tangentLength)
    addVec3(leftPoint, center, &directionToLeftPoint)

    cdef Vector3 directionToRightPoint
    scaleVec3(&directionToRightPoint, &rightDirection, tangentLength)
    addVec3(rightPoint, center, &directionToRightPoint)

    cdef Vector3 directionToLeftLeftHandle
    scaleVec3(&directionToLeftLeftHandle, &leftDirection, handleLength)
    addVec3(leftLeftHandle, leftPoint, &directionToLeftLeftHandle)
    subVec3(leftRightHandle, leftPoint, &directionToLeftLeftHandle)

    cdef Vector3 directionToRightRightHandle
    scaleVec3(&directionToRightRightHandle, &rightDirection, handleLength)
    addVec3(rightRightHandle, rightPoint, &directionToRightRightHandle)
    subVec3(rightLeftHandle, rightPoint, &directionToRightRightHandle)

cdef BezierSpline bevelCyclicPolySpline(PolySpline spline, VirtualDoubleList bevelRadii):
    cdef int numberOfPoints = spline.points.length
    cdef int indexOfLastPoint = numberOfPoints - 1

    cdef int pointsAmount = numberOfPoints * 2
    cdef Vector3DList points = Vector3DList(length = pointsAmount)
    cdef Vector3DList leftHandles = Vector3DList(length = pointsAmount)
    cdef Vector3DList rightHandles = Vector3DList(length = pointsAmount)
    cdef FloatList radii = FloatList(length = pointsAmount)
    cdef FloatList tilts = FloatList(length = pointsAmount)

    # Bevel first point. Left point is the last one.
    cdef int leftIndex = 0
    cdef int rightIndex = 1
    bevelPart(spline.points.data + indexOfLastPoint,
              spline.points.data,
              spline.points.data + 1,
              bevelRadii.get(0),
              points.data + leftIndex,
              leftHandles.data + leftIndex,
              rightHandles.data + leftIndex,
              points.data + rightIndex,
              leftHandles.data + rightIndex,
              rightHandles.data + rightIndex)
    cdef float radius = spline.radii.data[0]
    radii.data[leftIndex] = radius
    radii.data[rightIndex] = radius
    cdef float tilt = spline.tilts.data[0]
    tilts.data[leftIndex] = tilt
    tilts.data[rightIndex] = tilt

    # Bevel last point. Right point is the first one.
    leftIndex = indexOfLastPoint * 2
    rightIndex = indexOfLastPoint * 2 + 1
    bevelPart(spline.points.data + indexOfLastPoint - 1,
              spline.points.data + indexOfLastPoint,
              spline.points.data,
              bevelRadii.get(indexOfLastPoint),
              points.data + leftIndex,
              leftHandles.data + leftIndex,
              rightHandles.data + leftIndex,
              points.data + rightIndex,
              leftHandles.data + rightIndex,
              rightHandles.data + rightIndex)
    radius = spline.radii.data[indexOfLastPoint]
    radii.data[leftIndex] = radius
    radii.data[rightIndex] = radius
    tilt = spline.tilts.data[indexOfLastPoint]
    tilts.data[leftIndex] = tilt
    tilts.data[rightIndex] = tilt

    # Bevel the rest of the points.
    cdef Py_ssize_t i
    for i in range(1, indexOfLastPoint):
        leftIndex = i * 2
        rightIndex = i * 2 + 1
        bevelPart(spline.points.data + i - 1,
                  spline.points.data + i,
                  spline.points.data + i + 1,
                  bevelRadii.get(i),
                  points.data + leftIndex,
                  leftHandles.data + leftIndex,
                  rightHandles.data + leftIndex,
                  points.data + rightIndex,
                  leftHandles.data + rightIndex,
                  rightHandles.data + rightIndex)
        radius = spline.radii.data[i]
        radii.data[leftIndex] = radius
        radii.data[rightIndex] = radius
        tilt = spline.tilts.data[i]
        tilts.data[leftIndex] = tilt
        tilts.data[rightIndex] = tilt

    return BezierSpline(points, leftHandles, rightHandles, radii, tilts, True, spline.materialIndex)

cdef BezierSpline bevelNonCyclicPolySpline(PolySpline spline, VirtualDoubleList bevelRadii):
    cdef int numberOfPoints = spline.points.length
    cdef int indexOfLastPoint = numberOfPoints - 1

    cdef int pointsAmount = numberOfPoints * 2 - 2
    cdef Vector3DList points = Vector3DList(length = pointsAmount)
    cdef Vector3DList leftHandles = Vector3DList(length = pointsAmount)
    cdef Vector3DList rightHandles = Vector3DList(length = pointsAmount)
    cdef FloatList radii = FloatList(length = pointsAmount)
    cdef FloatList tilts = FloatList(length = pointsAmount)

    # Set the first point and its handles to the first poly point.
    points.data[0] = spline.points.data[0]
    leftHandles.data[0] = spline.points.data[0]
    rightHandles.data[0] = spline.points.data[0]
    radii.data[0] = spline.radii.data[0]
    tilts.data[0] = spline.tilts.data[0]

    # Set the last point and its handles to the last poly point.
    cdef int index = indexOfLastPoint * 2 - 1
    points.data[index] = spline.points.data[indexOfLastPoint]
    leftHandles.data[index] = spline.points.data[indexOfLastPoint]
    rightHandles.data[index] = spline.points.data[indexOfLastPoint]
    radii.data[index] = spline.radii.data[indexOfLastPoint]
    tilts.data[index] = spline.tilts.data[indexOfLastPoint]

    # Bevel the rest of the points.
    cdef float radius
    cdef Py_ssize_t i
    cdef int leftIndex, rightIndex
    for i in range(1, indexOfLastPoint):
        leftIndex = i * 2 - 1
        rightIndex = i * 2
        bevelPart(spline.points.data + i - 1,
                  spline.points.data + i,
                  spline.points.data + i + 1,
                  bevelRadii.get(i),
                  points.data + leftIndex,
                  leftHandles.data + leftIndex,
                  rightHandles.data + leftIndex,
                  points.data + rightIndex,
                  leftHandles.data + rightIndex,
                  rightHandles.data + rightIndex)
        radius = spline.radii.data[i]
        radii.data[leftIndex] = radius
        radii.data[rightIndex] = radius
        tilt = spline.tilts.data[i]
        tilts.data[leftIndex] = tilt
        tilts.data[rightIndex] = tilt

    return BezierSpline(points, leftHandles, rightHandles, radii, tilts, False, spline.materialIndex)

def bevelPolySpline(PolySpline spline, VirtualDoubleList bevelRadii):
    if spline.points.length < 3:
        return BezierSpline(points = spline.points.copy(),
                            radii = spline.radii.copy(),
                            tilts = spline.tilts.copy(),
                            cyclic = spline.cyclic,
                            materialIndex = spline.materialIndex)

    if spline.cyclic:
        return bevelCyclicPolySpline(spline, bevelRadii)
    else:
        return bevelNonCyclicPolySpline(spline, bevelRadii)
