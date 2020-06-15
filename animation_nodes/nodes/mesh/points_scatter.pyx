import cython
from libc.math cimport sqrt, ceil
from ... math cimport Vector3
from ... algorithms.random_number_generators cimport XoShiRo256Plus, XoShiRo256StarStar
from ... data_structures cimport (
    LongList,
    FloatList,
    DoubleList,
    UIntegerList,
    Vector3DList,
    VirtualDoubleList,
    PolygonIndicesList
    )

def randomPointsScatter(Vector3DList vertices, PolygonIndicesList polygons, VirtualDoubleList weights,
                        bint useWeightForDensity, Py_ssize_t seed, Py_ssize_t pointAmount):
    cdef FloatList triWeights, triAreas
    cdef Py_ssize_t polyAmount
    polyAmount, triAreas, triWeights = calculateTriangleWeightsAreas(vertices, polygons, weights)

    cdef LongList distribution
    cdef Py_ssize_t expectedAmount
    distribution, expectedAmount = distributionOfPoints(polyAmount, triAreas, triWeights, useWeightForDensity,
                                                        seed, pointAmount)

    return sampleRandomPoints(vertices, polygons, distribution, seed, polyAmount, expectedAmount)

@cython.cdivision(True)
cdef calculateTriangleWeightsAreas(Vector3DList vertices, PolygonIndicesList polygons, VirtualDoubleList weights):
    cdef Py_ssize_t vertexAmount = vertices.length
    cdef float weightMax = 1
    cdef float weight
    cdef Py_ssize_t i

    for i in range(vertexAmount):
        weight = weights.get(i)
        if weight > weightMax: weightMax = weight

    cdef UIntegerList polyIndices = polygons.indices
    cdef UIntegerList polyStarts = polygons.polyStarts
    cdef Py_ssize_t polyAmount = polygons.getLength()
    cdef FloatList triAreas = FloatList(length = polyAmount)
    cdef FloatList triWeights = FloatList(length = polyAmount)
    cdef Py_ssize_t start, polyIndex1, polyIndex2, polyIndex3

    for i in range (polyAmount):
        start = polyStarts.data[i]
        polyIndex1 = polyIndices.data[start]
        polyIndex2 = polyIndices.data[start + 1]
        polyIndex3 = polyIndices.data[start + 2]

        triAreas.data[i] = triangleArea(vertices.data[polyIndex1], vertices.data[polyIndex2], vertices.data[polyIndex3])
        triWeights.data[i] = (weights.get(polyIndex1) + weights.get(polyIndex2) + weights.get(polyIndex3)) / weightMax / 3.0

    return polyAmount, triAreas, triWeights

@cython.cdivision(True)
cdef float triangleArea(Vector3 v1, Vector3 v2, Vector3 v3):
    cdef Vector3 vs1, vs2, vc
    vs1.x = v1.x - v3.x
    vs1.y = v1.y - v3.y
    vs1.z = v1.z - v3.z

    vs2.x = v2.x - v3.x
    vs2.y = v2.y - v3.y
    vs2.z = v2.z - v3.z

    vc.x = vs1.y * vs2.z - vs1.z * vs2.y
    vc.y = vs1.z * vs2.x - vs1.x * vs2.z
    vc.z = vs1.x * vs2.y - vs1.y * vs2.x
    return sqrt(vc.x * vc.x + vc.y * vc.y + vc.z * vc.z) / 2.0

@cython.cdivision(True)
cdef distributionOfPoints(Py_ssize_t polyAmount, FloatList triAreas, FloatList triWeights,
                          bint useWeightForDensity, Py_ssize_t seed, Py_ssize_t pointAmount):
    # Initial distribution of points.
    cdef double triAreaTotal = 0
    cdef Py_ssize_t i
    for i in range(polyAmount):
        triAreaTotal += triAreas.data[i]

    if triAreaTotal == 0: triAreaTotal = 1
    triAreaTotal = pointAmount / triAreaTotal

    cdef LongList distribution = LongList(length = polyAmount)
    cdef Py_ssize_t currentAmount, triPointAmount
    currentAmount = 0
    if useWeightForDensity:
        for i in range(polyAmount):
            triPointAmount = int(ceil(triAreas.data[i] * triAreaTotal))
            distribution.data[i] = triPointAmount
            currentAmount += triPointAmount
    else:
        for i in range(polyAmount):
            triPointAmount = int(ceil(triAreas.data[i] * triAreaTotal * max(triWeights.data[i], 0)))
            distribution.data[i] = triPointAmount
            currentAmount += triPointAmount

    # If currentAmount is equal to pointAmount or zero.
    cdef Py_ssize_t expectedAmount = currentAmount
    if expectedAmount == pointAmount or currentAmount == 0:
        return distribution, expectedAmount

    # If currentAmount is not equal to pointAmount.
    expectedAmount = pointAmount
    cdef Py_ssize_t step, offsetAmount
    offsetAmount = abs(pointAmount - currentAmount)
    step = 1
    if currentAmount > pointAmount: step = -1

    cdef XoShiRo256StarStar rng = XoShiRo256StarStar(seed)
    cdef Py_ssize_t j
    for i in range(offsetAmount):
        for j in range(polyAmount):
            index = rng.nextIntWithMax(polyAmount)
            triPointAmount = distribution.data[index]
            if triPointAmount == 0: continue
            distribution.data[index] = triPointAmount + step
            break

    # Use weight as density.
    if useWeightForDensity:
        expectedAmount = 0
        for i in range(polyAmount):
            triPointAmount = int(ceil(distribution.data[i] * max(triWeights.data[i], 0)))
            distribution.data[i] = triPointAmount
            expectedAmount += triPointAmount
    return distribution, expectedAmount

cdef Vector3DList sampleRandomPoints(Vector3DList vertices, PolygonIndicesList polygons, LongList distribution,
                                     Py_ssize_t seed, Py_ssize_t polyAmount, Py_ssize_t expectedAmount):
    cdef DoubleList randomPoints = DoubleList(length = expectedAmount)
    cdef XoShiRo256Plus rng = XoShiRo256Plus(seed)
    cdef Py_ssize_t i
    for i in range(expectedAmount):
        randomPoints.data[i] = rng.nextDouble()

    cdef Vector3DList points = Vector3DList(length = expectedAmount)
    cdef UIntegerList polyLengths = polygons.polyLengths
    cdef UIntegerList polyStarts = polygons.polyStarts
    cdef UIntegerList polyIndices = polygons.indices
    cdef Py_ssize_t j, index, start
    cdef Vector3 v1, v2, v3, v
    cdef double p1, p2, p3
    index = 0
    for i in range(polyAmount):
        start = polyStarts.data[i]
        v1 = vertices.data[polyIndices.data[start]]
        v2 = vertices.data[polyIndices.data[start + 1]]
        v3 = vertices.data[polyIndices.data[start + 2]]
        for j in range(distribution.data[i]):
            p1 = randomPoints.data[index]
            p2 = randomPoints.data[expectedAmount - index - 1]
            if p1 + p2 > 1.0:
                p1 = 1.0 - p1
                p2 = 1.0 - p2
            p3 = 1.0 - p1 - p2

            v.x = p1 * v1.x + p2 * v2.x + p3 * v3.x
            v.y = p1 * v1.y + p2 * v2.y + p3 * v3.y
            v.z = p1 * v1.z + p2 * v2.z + p3 * v3.z
            points.data[index] = v
            index += 1

    return points
