from ... math cimport Vector3
from . c_utils import trianglePolygonsArea
from ... algorithms.random cimport randomDouble_Range
from ... data_structures cimport (
    LongList,
    FloatList,
    Vector3DList,
    VirtualDoubleList,
    PolygonIndicesList
    )

def randomPointsScatter(Vector3DList vertices, PolygonIndicesList polygons, VirtualDoubleList weights,
                        Py_ssize_t seed1, Py_ssize_t seed2, Py_ssize_t amount):

    cdef double area, areaMin
    cdef polyAmount = polygons.getLength()
    cdef FloatList areas = trianglePolygonsArea(vertices, polygons)
    cdef Py_ssize_t i
    areaMin = 1000000
    for i in range(polyAmount):
        area = areas.data[i]
        if areaMin > area and area > 0: areaMin = area

    cdef FloatList polyWeights = FloatList(length = polyAmount)
    cdef Vector3DList polyVertices = Vector3DList(length = polyAmount * 3)
    cdef double weight
    cdef Py_ssize_t k
    cdef Py_ssize_t j = 0
    for i in range(polyAmount):
        polygon  = polygons[i]
        weight = 0.
        for k in range(len(polygon)):
            index = polygon[k]
            weight += weights.get(index) / 3.
            polyVertices.data[j] = vertices.data[index]
            j += 1
        polyWeights.data[i] = weight

    cdef LongList probabilities = LongList()
    for i in range(polyAmount):
        area  = areas.data[i]
        for j in range(int(area * polyWeights.data[i] / areaMin)):
            probabilities.append(i)

    cdef Py_ssize_t lenProb = probabilities.getLength()
    if lenProb == 0: return Vector3DList()

    cdef Py_ssize_t seed = (seed1 * 674523 + seed2 * 3465284) % 0x7fffffff
    cdef LongList polyPoints = LongList(length = polyAmount)
    polyPoints.fill(0)
    for i in range(amount):
        polyPoints.data[probabilities.data[int(randomDouble_Range(seed + i, 0, lenProb))]] += 1

    cdef double p1, p2, p3
    cdef Vector3 v1, v2, v3, v
    cdef Vector3DList points = Vector3DList(length = amount)
    k = 0
    index = 0
    for i in range(polyAmount):
        index = 3 * i
        v1 = polyVertices.data[0 + index]
        v2 = polyVertices.data[1 + index]
        v3 = polyVertices.data[2 + index]
        for j in range(polyPoints.data[i]):
            p1 = randomDouble_Range(seed + i + j, 0, 1)
            p2 = randomDouble_Range(seed + i + j + 100, 0, 1)
            if p1 + p2 > 1:
                p1 = 1 - p1
                p2 = 1 - p2
            p3 = 1 - p1 - p2

            v.x = p1 * v1.x + p2 * v2.x + p3 * v3.x
            v.y = p1 * v1.y + p2 * v2.y + p3 * v3.y
            v.z = p1 * v1.z + p2 * v2.z + p3 * v3.z
            points.data[k] = v
            k += 1
    return points
