from libc.math cimport sqrt
from ... math cimport Vector3
from ... algorithms.random cimport randomDouble_Range
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
                        Py_ssize_t seed, Py_ssize_t pointAmount):
    cdef FloatList triWeights, triAreas
    cdef Py_ssize_t triAmount
    triAmount, triAreas, triWeights = calculateTriangleWeightsAreas(vertices, polygons, weights)

    cdef LongList distribution = trianglesDistribution(triAmount, triAreas, triWeights)
    cdef Py_ssize_t distLength = distribution.getLength()
    if distLength == 0: return Vector3DList()

    cdef LongList totalTriPoints = totalPointsOnTriangles(distribution, distLength, seed, triAmount, pointAmount)
    return sampleRandomPoints(vertices, polygons, totalTriPoints, distLength, seed, pointAmount)

cdef calculateTriangleWeightsAreas(Vector3DList vertices, PolygonIndicesList polygons, VirtualDoubleList weights):
    cdef UIntegerList polyLengths = polygons.polyLengths
    cdef Py_ssize_t polyAmount = polygons.getLength()
    cdef Py_ssize_t i, triAmount, polyLength

    triAmount = 0
    for i in range(polyAmount):
        polyLength = polyLengths.data[i]
        if polyLength > 3:
            triAmount += polyLength - 2
        else:
            triAmount += 1

    cdef Py_ssize_t j, triangleIndex, start, polyIndex1, polyIndex2, polyIndex3
    cdef FloatList triWeights = FloatList(length = triAmount)
    cdef FloatList triAreas = FloatList(length = triAmount)
    cdef UIntegerList polyStarts = polygons.polyStarts
    cdef UIntegerList polyIndices = polygons.indices
    cdef Vector3 vectorStart
    cdef double weightStart
    triangleIndex = 0
    for i in range (polyAmount):
        start = polyStarts.data[i]
        polyIndex1 = polyIndices.data[start]
        vectorStart = vertices.data[polyIndex1]
        weightStart = weights.get(polyIndex1)
        for j in range(polyLengths.data[i] - 2):
            polyIndex2 = polyIndices.data[start + 1 + j]
            polyIndex3 = polyIndices.data[start + 2 + j]

            triAreas.data[triangleIndex] = triangleArea(vectorStart, vertices.data[polyIndex2], vertices.data[polyIndex3])
            triWeights.data[triangleIndex] = (weightStart + weights.get(polyIndex2) + weights.get(polyIndex3)) / 3.0
            triangleIndex += 1
    return triAmount, triAreas, triWeights

cdef triangleArea(Vector3 v1, Vector3 v2, Vector3 v3):
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

cdef trianglesDistribution(Py_ssize_t triAmount, FloatList triAreas, FloatList triWeights):
    cdef double triAreaMin, triArea
    cdef Py_ssize_t i
    triAreaMin = triAreas.getMaxValue()
    for i in range(triAmount):
        triArea = triAreas.data[i]
        if triArea > 0 and triArea < triAreaMin: triAreaMin = triArea

    cdef LongList distribution = LongList()
    cdef Py_ssize_t j
    for i in range(triAmount):
        for j in range(int(triAreas.data[i] * triWeights.data[i] / triAreaMin)): distribution.append(i)
    return distribution

cdef totalPointsOnTriangles(LongList distribution, Py_ssize_t distLength, Py_ssize_t seed, Py_ssize_t triAmount,
                            Py_ssize_t pointAmount):
    cdef LongList totalTriPoints = LongList.fromValue(0, length = triAmount)
    cdef Py_ssize_t i
    for i in range(pointAmount):
        totalTriPoints.data[distribution.data[int(randomDouble_Range(i + seed, 0, distLength))]] += 1
    return totalTriPoints

cdef sampleRandomPoints(Vector3DList vertices, PolygonIndicesList polygons, LongList totalTriPoints,
                        Py_ssize_t distLength, Py_ssize_t seed, Py_ssize_t pointAmount):
    cdef DoubleList randomPoints = DoubleList(length = pointAmount)
    cdef Py_ssize_t i
    for i in range(pointAmount):
        randomPoints.data[i] = randomDouble_Range(i + seed, 0.0, 1.0)

    cdef Py_ssize_t j, k, index, triangleIndex, start, polyIndex1, polyIndex2, polyIndex3
    cdef Vector3DList points = Vector3DList(length = pointAmount)
    cdef UIntegerList polyLengths = polygons.polyLengths
    cdef UIntegerList polyStarts = polygons.polyStarts
    cdef Py_ssize_t polyAmount = polygons.getLength()
    cdef UIntegerList polyIndices = polygons.indices
    cdef Vector3 v1, v2, v3, v
    cdef double p1, p2, p3
    index = 0
    triangleIndex = 0
    for i in range(polyAmount):
        start = polyStarts.data[i]
        polyIndex1 = polyIndices.data[start]
        v1 = vertices.data[polyIndex1]
        for j in range(polyLengths.data[i] - 2):
            polyIndex2 = polyIndices.data[start + 1 + j]
            polyIndex3 = polyIndices.data[start + 2 + j]

            v2 = vertices.data[polyIndex2]
            v3 = vertices.data[polyIndex3]
            for k in range(totalTriPoints.data[triangleIndex]):
                p1 = randomPoints.data[index]
                p2 = randomPoints.data[pointAmount - index - 1]
                if p1 + p2 > 1.0:
                    p1 = 1.0 - p1
                    p2 = 1.0 - p2
                p3 = 1.0 - p1 - p2

                v.x = p1 * v1.x + p2 * v2.x + p3 * v3.x
                v.y = p1 * v1.y + p2 * v2.y + p3 * v3.y
                v.z = p1 * v1.z + p2 * v2.z + p3 * v3.z
                points.data[index] = v
                index += 1
            triangleIndex += 1
    return points
