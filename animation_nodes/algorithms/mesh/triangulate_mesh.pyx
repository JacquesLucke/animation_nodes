import cython
from libc.math cimport sin, cos
from cpython.mem cimport PyMem_Malloc, PyMem_Free
from ... data_structures cimport (
    LongList, FloatList, Vector3DList, PolygonIndicesList)
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
        triAmount += polyLength - 2

    cdef unsigned int *oldIndices = polygons.indices.data
    cdef unsigned int *oldPolyStarts = polygons.polyStarts.data

    cdef PolygonIndicesList newPolygons = PolygonIndicesList(
                                          indicesAmount = 3 * triAmount,
                                          polygonAmount = triAmount)
    cdef unsigned int *newIndices = newPolygons.indices.data
    cdef unsigned int *newPolyStarts = newPolygons.polyStarts.data
    cdef unsigned int *newPolyLengths = newPolygons.polyLengths.data

    cdef Py_ssize_t j, index, triangleIndex, start

    index = 0
    triangleIndex = 0
    for i in range(polygonAmount):
        start = oldPolyStarts[i]
        for j in range(oldPolyLengths[i] - 2):
            newPolyStarts[triangleIndex] = index
            newPolyLengths[triangleIndex] = 3
            triangleIndex += 1

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

    cdef LongList neighbors
    cdef Vector3DList polyVertices
    cdef Vector3 v1, v2, v3
    cdef Py_ssize_t polyStart, triangleIndex, polyIndex
    cdef Py_ssize_t j, index, previousIndex, earIndex, nextIndex
    cdef float angle
    cdef Vertex* verticesData

    polyIndex = 0
    triangleIndex = 0
    for i in range(polygonAmount):
        polyStart = oldPolyStarts[i]
        polyLength = oldPolyLengths[i]

        neighbors = LongList(length = polyLength)
        for j in range(polyLength):
            neighbors.data[j] = oldIndices[polyStart + j]

        polyVertices = projectPolygonVertices(vertices, neighbors)
        if not polyCounterClockwise(polyVertices):
            neighbors = neighbors.reversed()
            polyVertices = polyVertices.reversed()

        # Initialization of polygon's vertices.
        verticesData = <Vertex*>PyMem_Malloc(polyLength * sizeof(Vertex))
        for j in range(polyLength):
            previousIndex = (polyLength + j - 1) % polyLength
            earIndex = j
            nextIndex = (j + 1) % polyLength

            v1 = polyVertices.data[previousIndex]
            v2 = polyVertices.data[earIndex]
            v3 = polyVertices.data[nextIndex]

            verticesData[j].index = neighbors.data[earIndex]
            angle = calculateAngleWithSign(v1, v2, v3)
            verticesData[j].angle = angle
            if angle >= 0.0 and not pointsInTriangle(polyVertices, v1, v2, v3, previousIndex, earIndex, nextIndex):
                verticesData[j].isEar = True
            else:
                verticesData[j].isEar = False
            verticesData[j].previous = previousIndex
            verticesData[j].next = nextIndex

        # Calculate the triangle polygon indices.
        for j in range(polyLength - 2):
            if polyLength - 2 - j == 1:
                newPolyStarts[triangleIndex] = polyIndex
                newPolyLengths[triangleIndex] = 3
                triangleIndex += 1

                index = 0
                for k in range(polyLength):
                    if verticesData[k].isEar:
                        newIndices[polyIndex + index] = verticesData[k].index
                        index += 1
                        if index == 3: break
                polyIndex += 3
                break

            # Removing an ear which has smallest inner-angle.
            earIndex = findAngleMinIndex(polyLength, verticesData)
            previousIndex = verticesData[earIndex].previous
            nextIndex = verticesData[earIndex].next

            removeEarVertex(verticesData, polyVertices, previousIndex, earIndex, nextIndex)

            newPolyStarts[triangleIndex] = polyIndex
            newPolyLengths[triangleIndex] = 3
            triangleIndex += 1

            newIndices[polyIndex] = neighbors.data[previousIndex]
            newIndices[polyIndex + 1] = neighbors.data[earIndex]
            newIndices[polyIndex + 2] = neighbors.data[nextIndex]
            polyIndex += 3

        PyMem_Free(verticesData)

    return newPolygons

# Remove ear-vertex and update the neighbor-vertices.
cdef Vertex* removeEarVertex(Vertex* verticesData, Vector3DList polyVertices, Py_ssize_t previousIndex, Py_ssize_t earIndex, Py_ssize_t nextIndex):
    cdef Py_ssize_t previousPreviousIndex, nextNextIndex
    cdef Vector3 v0, v1, v2, v3, v4
    cdef float angle

    v1 = polyVertices.data[previousIndex]
    v2 = polyVertices.data[earIndex]
    v3 = polyVertices.data[nextIndex]

    previousPreviousIndex = verticesData[previousIndex].previous
    v0 = polyVertices.data[previousPreviousIndex]
    angle = calculateAngleWithSign(v0, v1, v3)
    verticesData[previousIndex].angle = angle
    if angle >= 0.0 and not pointsInTriangle(polyVertices, v0, v1, v3, previousPreviousIndex, previousIndex, nextIndex):
        verticesData[previousIndex].isEar = True
    else:
        verticesData[previousIndex].isEar = False

    nextNextIndex = verticesData[nextIndex].next
    v4 = polyVertices.data[nextNextIndex]
    angle = calculateAngleWithSign(v1, v3, v4)
    verticesData[nextIndex].angle = angle
    if angle >= 0.0 and not pointsInTriangle(polyVertices, v1, v3, v4, previousIndex, nextIndex, nextNextIndex):
        verticesData[nextIndex].isEar = True
    else:
        verticesData[nextIndex].isEar = False

    verticesData[earIndex].isEar = False
    verticesData[nextIndex].previous = previousIndex
    verticesData[previousIndex].next = nextIndex

cdef struct Vertex:
    Py_ssize_t index
    float angle
    bint isEar
    Py_ssize_t previous
    Py_ssize_t next

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

# Calculate inner angle.
cdef float calculateAngleWithSign(Vector3 v1, Vector3 v2, Vector3 v3):
    cdef Vector3 ab, bc
    cdef float angle

    subVec3(&ab, &v2, &v1)
    subVec3(&bc, &v2, &v3)

    normalizeVec3_InPlace(&ab)
    normalizeVec3_InPlace(&bc)

    angle = angleNormalizedVec3(&ab, &bc)

    # Make sure normal (+z) is correct, and the polygon is counter clockwise. Convex vertex has sign >= 0.
    cdef float sign = (v2.x - v1.x) * (v3.y - v1.y) - (v2.y - v1.y) * (v3.x - v1.x)
    if sign < 0.0: return -(angle - angle % 0.001)
    return (angle - angle % 0.001)

# Find the index of minimum angle.
cdef int findAngleMinIndex(Py_ssize_t polyLength, Vertex* verticesData):
    cdef float angleMin = 3.14
    cdef float angle
    cdef Py_ssize_t i, angleMinIndex

    angleMinIndex = 0
    for i in range(polyLength):
        if verticesData[i].isEar:
            angle = abs(verticesData[i].angle)
            if angleMin > angle:
                angleMin = angle
                angleMinIndex = i

    return angleMinIndex

# Checking points (reflex type) lies in the new triangle.
cdef bint pointsInTriangle(Vector3DList vertices, Vector3 v1, Vector3 v2, Vector3 v3,
                      Py_ssize_t previousIndex, Py_ssize_t earIndex, Py_ssize_t nextIndex):
    cdef Py_ssize_t i
    for i in range(vertices.length):
        if i != previousIndex and i != earIndex and i != nextIndex and pointInsideTriangle(v1, v2, v3, vertices.data[i]):
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
