import cython
from libc.stdlib cimport qsort
from libc.math cimport sin, cos, pi
from ... data_structures cimport (
    LongList, Vector3DList, PolygonIndicesList)
from ... math cimport (
    Vector3, crossVec3, subVec3, dotVec3, toVector3, lengthVec3,
    angleNormalizedVec3, normalizeVec3_InPlace
)

def triangulatePolygonsUsingFanSpanMethod(PolygonIndicesList polygons):
    cdef unsigned int *oldPolyLengths = polygons.polyLengths.data
    cdef Py_ssize_t polygonAmount = polygons.getLength()
    cdef Py_ssize_t i, triAmount, polyLength

    triAmount = 0
    for i in range(polygonAmount):
        polyLength = oldPolyLengths[i]
        if polyLength > 3:
            triAmount += polyLength - 2
        else:
            triAmount += 1

    cdef unsigned int *oldIndices = polygons.indices.data
    cdef unsigned int *oldPolyStarts = polygons.polyStarts.data

    cdef PolygonIndicesList newPolygons = PolygonIndicesList(
                                          indicesAmount = 3 * triAmount,
                                          polygonAmount = triAmount)
    cdef unsigned int *newIndices = newPolygons.indices.data
    cdef unsigned int *newPolyStarts = newPolygons.polyStarts.data
    cdef unsigned int *newPolyLengths = newPolygons.polyLengths.data

    cdef Py_ssize_t j, index, triIndex, start

    index = 0
    triIndex = 0
    for i in range(polygonAmount):
        start = oldPolyStarts[i]
        for j in range(oldPolyLengths[i] - 2):
            newPolyStarts[triIndex] = index
            newPolyLengths[triIndex] = 3
            triIndex += 1

            newIndices[index] = oldIndices[start]
            newIndices[index + 1] = oldIndices[start + 1 + j]
            newIndices[index + 2] = oldIndices[start + 2 + j]
            index += 3

    return newPolygons

@cython.cdivision(True)
def triangulatePolygonsUsingEarClipMethod(Vector3DList vertices, PolygonIndicesList polygons):
    cdef unsigned int *oldPolyLengths = polygons.polyLengths.data
    cdef Py_ssize_t polygonAmount = polygons.getLength()
    cdef Py_ssize_t i, triAmount, polyLength

    # Total number of triangle polygons.
    triAmount = 0
    for i in range(polygonAmount):
        polyLength = oldPolyLengths[i]
        triAmount += polyLength - 2

    cdef unsigned int *oldIndices = polygons.indices.data
    cdef unsigned int *oldPolyStarts = polygons.polyStarts.data

    cdef PolygonIndicesList newPolygons = PolygonIndicesList(
                                          indicesAmount = 3 * triAmount,
                                          polygonAmount = triAmount)
    cdef unsigned int *newIndices = newPolygons.indices.data
    cdef unsigned int *newPolyStarts = newPolygons.polyStarts.data
    cdef unsigned int *newPolyLengths = newPolygons.polyLengths.data

    cdef LongList neighbors, angles, sortAngles, mask, earNeighbors, earNextNeighbors
    cdef Vector3 preVertex, earVertex, nexVertex, v1, v2, v3
    cdef Vector3DList polyVertices
    cdef Py_ssize_t polyStart, triIndex, polyIndex, triCount
    cdef Py_ssize_t j, k, index, preIndex, earIndex, nexIndex, prePreIndex, nexNexIndex

    triIndex = 0
    polyIndex = 0
    for i in range(polygonAmount):
        polyLength = oldPolyLengths[i]
        polyStart = oldPolyStarts[i]

        neighbors = LongList(length = polyLength)
        mask = LongList(length = polyLength)
        for j in range(polyLength):
            neighbors.data[j] = oldIndices[polyStart + j]
            mask.data[j] = 0

        polyVertices = projectPolygonVertices(vertices, neighbors)
        if not polyCounterClockwise(polyVertices):
            neighbors = neighbors.reversed()
            polyVertices = polyVertices.reversed()

        # Calculate inner-angle for all vertices of polygon.
        angles = LongList(length = polyLength)
        for j in range(polyLength):
            preVertex = polyVertices.data[(polyLength + j - 1) % polyLength]
            earVertex = polyVertices.data[j]
            nexVertex = polyVertices.data[(j + 1) % polyLength]
            angles.data[j] = calculateAngle(preVertex, earVertex, nexVertex)

        # Calculate the triangle polygon indices.
        triCount = 0
        for j in range(polyLength - 2):
            if polyLength - 2 - triCount == 1:
                newPolyStarts[triIndex] = polyIndex
                newPolyLengths[triIndex] = 3
                triIndex += 1

                index = 0
                for k in range(polyLength):
                    if mask.data[k] < 1:
                        newIndices[polyIndex + index] = neighbors.data[k]
                        index += 1
                        if index == 3: break
                polyIndex += 3

                break

            sortAngles = angles.copy()
            qsort(sortAngles.data, sortAngles.length, sizeof(long), &compare)

            # Removing an ear which has smallest inner-angle
            for k in range(polyLength):
                earIndex = angles.index(sortAngles.data[k])
                if mask.data[earIndex] < 1:
                    earNeighbors = earNeighborIndices(earIndex, polyLength, mask)
                    preIndex = earNeighbors.data[0]
                    nexIndex = earNeighbors.data[1]

                    v1 = polyVertices.data[preIndex]
                    v2 = polyVertices.data[earIndex]
                    v3 = polyVertices.data[nexIndex]
                    if convexVertex(v1, v2, v3) and not pointsInTriangle(polyVertices, v1, v2, v3, preIndex, earIndex, nexIndex):
                        earNextNeighbors = earNextNeighborIndices(earIndex, preIndex, nexIndex, polyLength, mask)
                        triCount += 1
                        mask.data[earIndex] = 1
                        angles.data[earIndex] = 361
                        angles.data[preIndex] = calculateAngle(polyVertices.data[earNextNeighbors.data[0]], v1, v3)
                        angles.data[nexIndex] = calculateAngle(v1, v3, polyVertices.data[earNextNeighbors.data[1]])

                        newPolyStarts[triIndex] = polyIndex
                        newPolyLengths[triIndex] = 3
                        triIndex += 1

                        newIndices[polyIndex] = neighbors.data[preIndex]
                        newIndices[polyIndex + 1] = neighbors.data[earIndex]
                        newIndices[polyIndex + 2] = neighbors.data[nexIndex]
                        polyIndex += 3

                        break

    return newPolygons

# Make sure normal (+z) is correct.
@cython.cdivision(True)
cdef bint polyCounterClockwise(Vector3DList vertices):
    cdef Py_ssize_t amount = vertices.length
    cdef float area = 0.0
    cdef Vector3 v1, v2
    cdef Py_ssize_t i

    for i in range(amount - 1):
        v1 = vertices.data[i]
        v2 = vertices.data[i + 1]
        area += (v2.x - v1.x) * (v2.y + v1.y)
    v1 = vertices.data[amount - 1]
    v2 = vertices.data[0]
    area += (v2.x - v1.x) * (v2.y + v1.y)

    if area > 0.0: return False
    return True

# Calculate Inner angle (degree).
cdef int calculateAngle(Vector3 preVertex, Vector3 earVertex, Vector3 nexVertex):
    cdef Vector3 ab, bc
    cdef float angle

    subVec3(&ab, &earVertex, &preVertex)
    subVec3(&bc, &earVertex, &nexVertex)

    normalizeVec3_InPlace(&ab)
    normalizeVec3_InPlace(&bc)

    angle = angleNormalizedVec3(&ab, &bc)
    return int((angle - angle % 0.001) * 180.0 / pi)

@cython.cdivision(True)
cdef LongList earNeighborIndices(Py_ssize_t earIndex, Py_ssize_t polyLength, LongList mask):
    cdef LongList indices = LongList(length = 2)
    cdef Py_ssize_t i, index
    for i in range(polyLength - 1):
        index = earIndex - 1 - i
        if index < 0: index += polyLength
        if mask.data[index] < 1:
            indices.data[0] = index
            break

    for i in range(polyLength - 1):
        index = (earIndex + 1 + i) % polyLength
        if mask.data[index] < 1:
            indices.data[1] = index
            break

    return indices

@cython.cdivision(True)
cdef LongList earNextNeighborIndices(Py_ssize_t earIndex, Py_ssize_t preIndex, Py_ssize_t nexIndex,
                                     Py_ssize_t polyLength, LongList mask):
    cdef LongList indices = LongList(length = 2)
    cdef Py_ssize_t i, index

    for i in range(polyLength - 1):
        index = earIndex - 2 - i
        if index < 0: index += polyLength
        if mask.data[index] < 1 and index != earIndex and index != preIndex and index != nexIndex:
            indices.data[0] = index
            break

    for i in range(polyLength - 1):
        index = (earIndex + 2 + i) % polyLength
        if mask.data[index] < 1 and index != earIndex and index != preIndex and index != nexIndex:
            indices.data[1] = index
            break

    return indices

# Make sure normal (+z) is correct, and the polygon is counter clockwise.
cdef bint convexVertex(Vector3 v1, Vector3 v2, Vector3 v3):
    cdef float sign = (v2.x - v1.x) * (v3.y - v1.y) - (v2.y - v1.y) * (v3.x - v1.x)
    if sign >= 0: return True
    return False

# Checking points (reflex type) lies in the new triangle.
cdef bint pointsInTriangle(Vector3DList vertices, Vector3 v1, Vector3 v2, Vector3 v3,
                      Py_ssize_t preIndex, Py_ssize_t earIndex, Py_ssize_t nexIndex):
    cdef Py_ssize_t i
    for i in range(vertices.length):
        if i != preIndex and i != earIndex and i != nexIndex and pointInsideTriangle(v1, v2, v3, vertices.data[i]):
            return True
    return False

@cython.cdivision(True)
cdef bint pointInsideTriangle(Vector3 v1, Vector3 v2, Vector3 v3, Vector3 p):
    cdef Vector3 u, v, w, n
    subVec3(&u, &v2, &v1)
    subVec3(&v, &v3, &v1)
    subVec3(&w, &p, &v1)

    cdef float delta = 0.00001
    v.x += delta
    v.y += delta
    v.z += delta

    crossVec3(&n, &u, &v)
    cdef float normSq = lengthVec3(&n)
    normSq = normSq * normSq

    cdef Vector3 uw, wv
    crossVec3(&uw, &u, &w)
    crossVec3(&wv, &w, &v)

    cdef float alpha = dotVec3(&uw, &n) / normSq
    cdef float beta = dotVec3(&wv, &n) / normSq
    cdef float gamma = 1.0 - alpha - beta
    if alpha >= 0.0 and alpha <= 1.0 and beta >= 0.0 and beta <= 1.0 and gamma >= 0.0 and gamma <= 1.0:
        return True
    else:
        return False

# Transformation of vertices of polygon into xy-plane.
@cython.cdivision(True)
cdef Vector3DList projectPolygonVertices(Vector3DList vertices, LongList polygonIndices):
    cdef Py_ssize_t polyLength = polygonIndices.length
    cdef Vector3DList polyVertices = Vector3DList(length = polyLength)

    # Compute polygon normal with Nowell's method.
    cdef Vector3 polyNormal = toVector3((0, 0, 0))
    cdef Py_ssize_t i
    for i in range(polyLength):
        v1 = vertices.data[polygonIndices.data[i]]
        v2 = vertices.data[polygonIndices.data[(i + 1) % polyLength]]

        polyNormal.x += (v1.y - v2.y) * (v1.z + v2.z)
        polyNormal.y += (v1.z - v2.z) * (v1.x + v2.x)
        polyNormal.z += (v1.x - v2.x) * (v1.y + v2.y)

        polyVertices.data[i] = v1
    normalizeVec3_InPlace(&polyNormal)

    # Calculate the coefficient for Rodrigues's rotation formula.
    cdef Vector3 zAxis = toVector3((0, 0, 1))
    cdef Vector3 rotAxis
    crossVec3(&rotAxis, &polyNormal, &zAxis)
    normalizeVec3_InPlace(&rotAxis)

    cdef float angle = angleNormalizedVec3(&polyNormal, &zAxis)
    cdef float sint = sin(angle)
    cdef float cost = cos(angle)
    cdef float fact = 1.0 - cost

    # Rotating vertices of polygon, and droping the z-comp.
    cdef Vector3DList rotPolyVertices = Vector3DList(length = polyLength)
    cdef Vector3 vertex, cross, rotPolyVertex
    cdef float dot
    for i in range(polyLength):
        vertex = polyVertices.data[i]
        crossVec3(&cross, &rotAxis, &vertex)
        dot = dotVec3(&rotAxis, &vertex)

        rotPolyVertex.x = cost * vertex.x + sint * cross.x + dot * fact * rotAxis.x
        rotPolyVertex.y = cost * vertex.y + sint * cross.y + dot * fact * rotAxis.y
        rotPolyVertex.z = cost * vertex.z + sint * cross.z + dot * fact * rotAxis.z
        rotPolyVertices.data[i].x = rotPolyVertex.x
        rotPolyVertices.data[i].y = rotPolyVertex.y
        rotPolyVertices.data[i].z = 0.0

    return rotPolyVertices

cdef int compare(const void * a, const void * b) nogil:
   return (<int*>a)[0] - (<int*>b)[0]
