import cython
from libc.math cimport sqrt, ceil
from ... algorithms.random_number_generators cimport XoShiRo256Plus, XoShiRo256StarStar
from ... data_structures cimport (
    LongList,
    FloatList,
    DoubleList,
    UIntegerList,
    Vector3DList,
    Matrix4x4List,
    EdgeIndicesList,
    VirtualDoubleList,
    PolygonIndicesList
)
from ... math cimport (
    Vector3,
    addVec3,
    subVec3,
    Matrix4,
    crossVec3,
    distanceVec3,
    normalizeVec3_InPlace,
    matrixFromNormalizedAxisData,
)

def scatterPointsOnPolygons(Vector3DList vertices, PolygonIndicesList polygons, Vector3DList polyNormals,
                        VirtualDoubleList weights, long seed, long numberOfPoints):
    cdef DoubleList triangleWeights = calculateTriangleWeights(vertices, polygons, weights)

    cdef LongList distribution
    cdef long computedNumberOfPoints
    distribution = computeDistribution(triangleWeights, numberOfPoints, seed, &computedNumberOfPoints)

    return sampleRandomPointsOnPolygons(vertices, polygons, polyNormals, distribution, computedNumberOfPoints, seed)

@cython.cdivision(True)
cdef DoubleList calculateTriangleWeights(Vector3DList vertices, PolygonIndicesList polygons, VirtualDoubleList weights):
    cdef DoubleList triangleWeights = DoubleList(length = polygons.getLength())
    cdef Py_ssize_t i, j, i1, i2, i3
    for i in range (polygons.getLength()):
        j = 3 * i
        i1 = polygons.indices.data[j]
        i2 = polygons.indices.data[j + 1]
        i3 = polygons.indices.data[j + 2]

        triangleWeights.data[i] = triangleArea(vertices.data + i1, vertices.data + i2, vertices.data + i3)
        triangleWeights.data[i] *= max((weights.get(i1) + weights.get(i2) + weights.get(i3)) / 3.0, 0)
    return triangleWeights

@cython.cdivision(True)
cdef double triangleArea(Vector3 *v1, Vector3 *v2, Vector3 *v3):
    cdef Vector3 vs1, vs2, vc
    vs1.x = v1[0].x - v3[0].x
    vs1.y = v1[0].y - v3[0].y
    vs1.z = v1[0].z - v3[0].z

    vs2.x = v2[0].x - v3[0].x
    vs2.y = v2[0].y - v3[0].y
    vs2.z = v2[0].z - v3[0].z

    vc.x = vs1.y * vs2.z - vs1.z * vs2.y
    vc.y = vs1.z * vs2.x - vs1.x * vs2.z
    vc.z = vs1.x * vs2.y - vs1.y * vs2.x
    return sqrt(vc.x * vc.x + vc.y * vc.y + vc.z * vc.z) / 2.0

@cython.cdivision(True)
cdef LongList computeDistribution(DoubleList triangleWeights, long numberOfPoints, long seed,
                                  long *outputNumberOfPoints):
    cdef long numberOfTriangles = triangleWeights.length
    cdef LongList distribution = LongList(length = numberOfTriangles)
    cdef long computedNumberOfPoints, triangleNumberOfPoints
    cdef Py_ssize_t i

    cdef double sumOfWeights = 0.0
    for i in range(numberOfTriangles):
        sumOfWeights += triangleWeights.data[i]

    if sumOfWeights == 0: sumOfWeights = 1
    cdef double numberOfPointsPerUnitWeight = numberOfPoints / sumOfWeights
    computedNumberOfPoints = 0
    for i in range(numberOfTriangles):
        triangleNumberOfPoints = <long>ceil(numberOfPointsPerUnitWeight * triangleWeights.data[i])
        distribution.data[i] = triangleNumberOfPoints
        computedNumberOfPoints += triangleNumberOfPoints

    if computedNumberOfPoints == 0:
        outputNumberOfPoints[0] = 0
        return distribution

    cdef XoShiRo256StarStar rng = XoShiRo256StarStar(seed)
    cdef Py_ssize_t randomIndex
    for i in range(computedNumberOfPoints - numberOfPoints):
        while True:
            randomIndex = rng.nextLongWithMax(numberOfTriangles)
            triangleNumberOfPoints = distribution.data[randomIndex]
            if triangleNumberOfPoints != 0:
                distribution.data[randomIndex] -= 1
                break

    outputNumberOfPoints[0] = numberOfPoints
    return distribution

cdef Matrix4x4List sampleRandomPointsOnPolygons(Vector3DList vertices, PolygonIndicesList polygons,
                                                Vector3DList polyNormals, LongList distribution,
                                                long numberOfPoints, long seed):
    cdef XoShiRo256Plus rng = XoShiRo256Plus(seed)
    cdef Matrix4x4List matrices = Matrix4x4List(length = numberOfPoints)
    cdef Vector3 v1, v2, v3, v, normal, tangent, bitangent
    cdef Py_ssize_t i, j, k, index
    cdef double p1, p2, p3
    index = 0
    for i in range(polygons.getLength()):
        j = i * 3
        v1 = vertices.data[polygons.indices.data[j]]
        v2 = vertices.data[polygons.indices.data[j + 1]]
        v3 = vertices.data[polygons.indices.data[j + 2]]

        normal = polyNormals.data[i]
        normalizeVec3_InPlace(&normal)

        subVec3(&tangent, &v1, &v2)
        normalizeVec3_InPlace(&tangent)

        crossVec3(&bitangent, &tangent, &normal)
        normalizeVec3_InPlace(&bitangent)

        for k in range(distribution.data[i]):
            p1 = rng.nextDouble()
            p2 = rng.nextDouble()
            if p1 + p2 > 1.0:
                p1 = 1.0 - p1
                p2 = 1.0 - p2
            p3 = 1.0 - p1 - p2

            v.x = p1 * v1.x + p2 * v2.x + p3 * v3.x
            v.y = p1 * v1.y + p2 * v2.y + p3 * v3.y
            v.z = p1 * v1.z + p2 * v2.z + p3 * v3.z

            matrixFromNormalizedAxisData(matrices.data + index, &v, &bitangent, &tangent, &normal)
            index += 1

    return matrices


def scatterPointsOnEdges(Vector3DList vertices, EdgeIndicesList edges, Vector3DList vertexNormals,
                         VirtualDoubleList weights, long seed, long numberOfPoints):
    cdef DoubleList edgeWeights = calculateEdgeWeights(vertices, edges, weights)

    cdef LongList distribution
    cdef long computedNumberOfPoints
    distribution = computeDistribution(edgeWeights, numberOfPoints, seed, &computedNumberOfPoints)

    return sampleRandomPointsOnEdges(vertices, edges, vertexNormals, distribution,
                                     computedNumberOfPoints, seed)

@cython.cdivision(True)
cdef DoubleList calculateEdgeWeights(Vector3DList vertices, EdgeIndicesList edges,
                                     VirtualDoubleList weights):
    cdef edgeAmount = edges.getLength()
    cdef DoubleList edgeWeights = DoubleList(length = edgeAmount)
    cdef Py_ssize_t i, i1, i2
    for i in range (edgeAmount):
        i1 = edges.data[i].v1
        i2 = edges.data[i].v2

        edgeWeights.data[i] = distanceVec3(vertices.data + i1, vertices.data + i2)
        edgeWeights.data[i] *= max((weights.get(i1) + weights.get(i2)) / 2.0, 0)
    return edgeWeights

cdef Matrix4x4List sampleRandomPointsOnEdges(Vector3DList vertices, EdgeIndicesList edges,
                                             Vector3DList vertexNormals, LongList distribution,
                                             long numberOfPoints, long seed):
    cdef XoShiRo256Plus rng = XoShiRo256Plus(seed)
    cdef Matrix4x4List matrices = Matrix4x4List(length = numberOfPoints)
    cdef Vector3 v, normal, tangent, bitangent
    cdef Vector3 *v1, *v2, *n1, *n2
    cdef Py_ssize_t i, j, index
    cdef double p1, p2
    index = 0
    for i in range(edges.getLength()):
        v1 = vertices.data + edges.data[i].v1
        v2 = vertices.data + edges.data[i].v2

        n1 = vertexNormals.data + edges.data[i].v1
        n2 = vertexNormals.data + edges.data[i].v2
        addVec3(&normal, n1, n2)
        normalizeVec3_InPlace(&normal)

        subVec3(&tangent, v1, v2)
        normalizeVec3_InPlace(&tangent)

        crossVec3(&bitangent, &tangent, &normal)
        normalizeVec3_InPlace(&bitangent)

        for j in range(distribution.data[i]):
            p1 = rng.nextDouble()
            p2 = 1.0 - p1

            v.x = p1 * v1[0].x + p2 * v2[0].x
            v.y = p1 * v1[0].y + p2 * v2[0].y
            v.z = p1 * v1[0].z + p2 * v2[0].z

            matrixFromNormalizedAxisData(matrices.data + index, &v, &bitangent, &tangent, &normal)
            index += 1

    return matrices
