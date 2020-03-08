from libc.math cimport sqrt
from ... math cimport Vector3
from ... algorithms.random cimport randomDouble_Range
from ... data_structures cimport (
    LongList,
    FloatList,
    UIntegerList,
    Vector3DList,
    VirtualDoubleList,
    PolygonIndicesList
    )

def randomPointsScatter(Vector3DList vertices, PolygonIndicesList polygons, VirtualDoubleList weights,
                        Py_ssize_t seed1, Py_ssize_t seed2, Py_ssize_t amount):
    cdef Vector3DList triVertices
    cdef FloatList triWeights, triAreas
    cdef Py_ssize_t triAmount
    cdef double triAreaMin
    triAmount, triVertices, triWeights, triAreas, triAreaMin = calculateTriangleVerticesWeightsAreas(vertices,
                                                                                                  polygons,
                                                                                                  weights)

    cdef LongList probabilities = cumulativeProbabilities(triAreaMin, triAreas, triWeights, triAmount)
    cdef Py_ssize_t lenProb = probabilities.getLength()
    if lenProb == 0: return Vector3DList()

    cdef Py_ssize_t seed = (seed1 * 674523 + seed2 * 3465284) % 0x7fffffff
    cdef LongList polyPoints = pointsOnTriangles(probabilities, lenProb, seed, triAmount, amount)

    return sampleRandomPoints(triVertices, polyPoints, lenProb, seed, triAmount, amount)

def calculateTriangleVerticesWeightsAreas(Vector3DList vertices, PolygonIndicesList polygons, VirtualDoubleList weights):
    cdef Vector3DList triangleVertices = Vector3DList(length = 3)
    cdef UIntegerList polyLengths = polygons.polyLengths
    cdef Vector3DList triVertices = Vector3DList()
    cdef Py_ssize_t amount = polygons.getLength()
    cdef FloatList triWeights = FloatList()
    cdef FloatList triAreas = FloatList()
    cdef double triArea, triAreaMin
    cdef Vector3 v1, v2, v3
    cdef Py_ssize_t i, j, index1, index2, index3, polyLength, triAmount

    triAmount = 0
    triAreaMin = 1000000.
    for i in range (amount):
        polygon = polygons[i]
        polyLength = polyLengths.data[i]
        if polyLength > 3:
            index1 = polygon[0]
            v1 = vertices.data[index1]
            for j in range(polyLength - 2):
                triAmount += 1
                index2 = polygon[1 + j]
                index3 = polygon[2 + j]

                v2 = vertices.data[index2]
                v3 = vertices.data[index3]

                triangleVertices.data[0] = v1
                triangleVertices.data[1] = v2
                triangleVertices.data[2] = v3
                triVertices.extend(triangleVertices)

                triWeights.append((weights.get(index1) + weights.get(index2) + weights.get(index3)) / 3.0)

                triArea = triangleArea(v1, v2, v3)
                triAreas.append(triArea)
                if triAreaMin > triArea and triArea > 0: triAreaMin = triArea
        else:
            triAmount += 1
            index1 = polygon[0]
            index2 = polygon[1]
            index3 = polygon[2]

            v1 = vertices.data[index1]
            v2 = vertices.data[index2]
            v3 = vertices.data[index3]

            triangleVertices.data[0] = v1
            triangleVertices.data[1] = v2
            triangleVertices.data[2] = v3
            triVertices.extend(triangleVertices)

            triWeights.append((weights.get(index1) + weights.get(index2) + weights.get(index3)) / 3.0)

            triArea = triangleArea(v1, v2, v3)
            triAreas.append(triArea)
            if triAreaMin > triArea and triArea > 0: triAreaMin = triArea
    return triAmount, triVertices, triWeights, triAreas, triAreaMin

def cumulativeProbabilities(double triAreaMin, FloatList triAreas, FloatList triWeights, Py_ssize_t triAmount):
    cdef LongList probabilities = LongList()
    cdef Py_ssize_t i, j
    for i in range(triAmount):
        for j in range(int(triAreas.data[i] * triWeights.data[i] / triAreaMin)): probabilities.append(i)
    return probabilities

def pointsOnTriangles(LongList probabilities, Py_ssize_t lenProb, Py_ssize_t seed, Py_ssize_t triAmount,
                             Py_ssize_t amount):
    cdef LongList polyPoints = LongList(length = triAmount)
    cdef Py_ssize_t i
    polyPoints.fill(0)
    for i in range(amount):
        polyPoints.data[probabilities.data[int(randomDouble_Range(seed + i, 0, lenProb))]] += 1
    return polyPoints

def sampleRandomPoints(Vector3DList triVertices, LongList polyPoints, Py_ssize_t lenProb, Py_ssize_t seed,
                       Py_ssize_t triAmount, Py_ssize_t amount):
    cdef Vector3DList points = Vector3DList(length = amount)
    cdef Py_ssize_t i, j, k, index, randSeed
    cdef Vector3 v1, v2, v3, v
    cdef double p1, p2, p3
    index = 0
    k = 0

    for i in range(triAmount):
        index = 3 * i
        v1 = triVertices.data[0 + index]
        v2 = triVertices.data[1 + index]
        v3 = triVertices.data[2 + index]
        randSeed = int(randomDouble_Range(seed + index, 0, lenProb))
        for j in range(polyPoints.data[i]):
            p1 = randomDouble_Range(seed + i + j + randSeed, 0.0, 1.0)
            p2 = randomDouble_Range(2 * seed + i + j + randSeed, 0.0, 1.0)
            if p1 + p2 > 1.0:
                p1 = 1.0 - p1
                p2 = 1.0 - p2
            p3 = 1.0 - p1 - p2

            v.x = p1 * v1.x + p2 * v2.x + p3 * v3.x
            v.y = p1 * v1.y + p2 * v2.y + p3 * v3.y
            v.z = p1 * v1.z + p2 * v2.z + p3 * v3.z
            points.data[k] = v
            k += 1
    return points

def triangleArea(Vector3 v1, Vector3 v2, Vector3 v3):
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

    return sqrt(vc.x * vc.x + vc.y * vc.y + vc.z * vc.z)/2.
