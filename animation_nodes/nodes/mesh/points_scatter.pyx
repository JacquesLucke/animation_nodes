import cython
from libc.math cimport sqrt
from ... math cimport Vector3
from ... algorithms.random_number_generators cimport XoShiRo256Plus
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
                        bint useWeightForDensity, Py_ssize_t seed, Py_ssize_t pointAmount, Py_ssize_t resolution):
    cdef FloatList triWeights, triAreas
    cdef Py_ssize_t polyAmount
    polyAmount, triAreas, triWeights = calculateTriangleWeightsAreas(vertices, polygons, weights)

    cdef LongList distribution = trianglesDistribution(polyAmount, triAreas, triWeights, useWeightForDensity,
                                                       resolution)
    cdef Py_ssize_t distLength = distribution.getLength()
    if distLength == 0: return Vector3DList()

    cdef LongList totalTriPoints
    cdef Py_ssize_t newPointAmount
    cdef XoShiRo256Plus rng = XoShiRo256Plus(seed)
    totalTriPoints, newPointAmount = totalPointsOnTriangles(rng, distribution, distLength, triWeights, useWeightForDensity,
                                                            seed, polyAmount, pointAmount)
    return sampleRandomPoints(rng, vertices, polygons, totalTriPoints, distLength, seed, polyAmount, newPointAmount)

@cython.cdivision(True)
cdef calculateTriangleWeightsAreas(Vector3DList vertices, PolygonIndicesList polygons, VirtualDoubleList weights):
    cdef Py_ssize_t vertexAmount = vertices.length
    cdef float weightMax = 1
    cdef float weightCurrent
    cdef Py_ssize_t i

    for i in range(vertexAmount):
        weightCurrent = weights.get(i)
        if weightCurrent > weightMax: weightMax = weightCurrent

    if weightMax == 0: weightMax = 1

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
cdef LongList trianglesDistribution(Py_ssize_t polyAmount, FloatList triAreas, FloatList triWeights, bint useWeightForDensity,
                                    Py_ssize_t resolution):
    cdef double triAreaMin, triArea
    cdef Py_ssize_t i
    triAreaMin = triAreas.getMaxValue()
    for i in range(polyAmount):
        triArea = triAreas.data[i]
        if triArea > 0 and triArea < triAreaMin: triAreaMin = triArea

    cdef LongList distribution = LongList()
    cdef Py_ssize_t j
    if useWeightForDensity:
        for i in range(polyAmount):
            for j in range(int(triAreas.data[i] / triAreaMin)): distribution.append(i)
        return distribution

    for i in range(polyAmount):
        for j in range(int(triAreas.data[i] * triWeights.data[i] * resolution / triAreaMin)): distribution.append(i)
    return distribution

cdef totalPointsOnTriangles(XoShiRo256Plus rng, LongList distribution, Py_ssize_t distLength, FloatList triWeights,
                            bint useWeightForDensity, Py_ssize_t seed, Py_ssize_t polyAmount, Py_ssize_t pointAmount):
    cdef LongList totalTriPoints = LongList.fromValue(0, length = polyAmount)
    cdef Py_ssize_t i
    for i in range(pointAmount):
        totalTriPoints.data[distribution.data[int(rng.nextDoubleInRange(0, distLength))]] += 1

    cdef Py_ssize_t newPointAmount = pointAmount
    cdef Py_ssize_t amount
    if useWeightForDensity:
        newPointAmount = 0
        for i in range(polyAmount):
            amount = int(totalTriPoints.data[i] * triWeights.data[i])
            totalTriPoints.data[i] = amount
            newPointAmount += amount
    return totalTriPoints, newPointAmount

cdef Vector3DList sampleRandomPoints(XoShiRo256Plus rng, Vector3DList vertices, PolygonIndicesList polygons, LongList totalTriPoints,
                                     Py_ssize_t distLength, Py_ssize_t seed, Py_ssize_t polyAmount, Py_ssize_t newPointAmount):
    cdef DoubleList randomPoints = DoubleList(length = newPointAmount)
    cdef Py_ssize_t i
    for i in range(newPointAmount):
        randomPoints.data[i] = rng.nextDoubleInRange(0.0, 1.0)

    cdef Vector3DList points = Vector3DList(length = newPointAmount)
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
        for j in range(totalTriPoints.data[i]):
            p1 = randomPoints.data[index]
            p2 = randomPoints.data[newPointAmount - index - 1]
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
