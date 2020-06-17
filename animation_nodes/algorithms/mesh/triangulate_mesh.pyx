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

        # Initialization of polygon's vertices.
        verticesData = <Vertex*>PyMem_Malloc(polyLength * sizeof(Vertex))
        projectPolygonVertices(vertices, polyStart, polyLength, oldIndices, verticesData)

        if not polyCounterClockwise(verticesData):
            for j in range(polyLength):
                previousIndex = verticesData[j].previous
                nextIndex = verticesData[j].next
                verticesData[j].previous = nextIndex
                verticesData[j].next = previousIndex

        for j in range(polyLength):
            earIndex = j
            previousIndex = verticesData[earIndex].previous
            nextIndex = verticesData[earIndex].next

            v1 = verticesData[previousIndex].location
            v2 = verticesData[earIndex].location
            v3 = verticesData[nextIndex].location

            angle = calculateAngleWithSign(verticesData, earIndex)
            verticesData[j].angle = angle
            if angle >= 0.0 and not pointsInTriangle(polyLength, verticesData, earIndex):
                verticesData[j].isEar = True
            else:
                verticesData[j].isEar = False

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
            earIndex = findEarHasMinAngle(polyLength, verticesData)

            newPolyStarts[triangleIndex] = polyIndex
            newPolyLengths[triangleIndex] = 3
            triangleIndex += 1

            newIndices[polyIndex] = verticesData[verticesData[earIndex].previous].index
            newIndices[polyIndex + 1] = verticesData[earIndex].index
            newIndices[polyIndex + 2] = verticesData[verticesData[earIndex].next].index
            polyIndex += 3

            removeEarVertex(polyLength, verticesData, earIndex)

        PyMem_Free(verticesData)

    return newPolygons

# Remove ear-vertex and update the neighbor-vertices.
cdef void removeEarVertex(Py_ssize_t polyLength, Vertex* verticesData, Py_ssize_t earIndex):
    cdef Py_ssize_t previousIndex, nextIndex
    previousIndex = verticesData[earIndex].previous
    nextIndex = verticesData[earIndex].next

    verticesData[earIndex].isEar = False
    verticesData[nextIndex].previous = previousIndex
    verticesData[previousIndex].next = nextIndex

    cdef float angle
    angle = calculateAngleWithSign(verticesData, previousIndex)
    verticesData[previousIndex].angle = angle
    if angle >= 0.0 and not pointsInTriangle(polyLength, verticesData, previousIndex):
        verticesData[previousIndex].isEar = True
    else:
        verticesData[previousIndex].isEar = False

    angle = calculateAngleWithSign(verticesData, nextIndex)
    verticesData[nextIndex].angle = angle
    if angle >= 0.0 and not pointsInTriangle(polyLength, verticesData, nextIndex):
        verticesData[nextIndex].isEar = True
    else:
        verticesData[nextIndex].isEar = False

cdef struct Vertex:
    Py_ssize_t index
    Vector3 location
    float angle
    bint isEar
    Py_ssize_t previous
    Py_ssize_t next

# Make sure normal (+z) is correct.
@cython.cdivision(True)
cdef bint polyCounterClockwise(Vertex* verticesData):
    cdef Vector3 v1, v2
    cdef float area = 0.0
    cdef Py_ssize_t headIndex = 0
    cdef Py_ssize_t currentIndex

    currentIndex = headIndex
    while(True):
        v1 = verticesData[currentIndex].location
        currentIndex = verticesData[currentIndex].next
        v2 = verticesData[currentIndex].location
        area += (v2.x - v1.x) * (v2.y + v1.y)
        if currentIndex == headIndex: break

    if area > 0.0: return False
    return True

# Calculate inner angle.
cdef float calculateAngleWithSign(Vertex* verticesData, Py_ssize_t index):
    cdef Vector3 v1 = verticesData[verticesData[index].previous].location
    cdef Vector3 v2 = verticesData[index].location
    cdef Vector3 v3 = verticesData[verticesData[index].next].location
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
cdef int findEarHasMinAngle(Py_ssize_t polyLength, Vertex* verticesData):
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
cdef bint pointsInTriangle(Py_ssize_t polyLength, Vertex* verticesData, Py_ssize_t earIndex):
    cdef Py_ssize_t previousIndex = verticesData[earIndex].previous
    cdef Py_ssize_t nextIndex = verticesData[earIndex].next

    cdef Vector3 v1 = verticesData[previousIndex].location
    cdef Vector3 v2 = verticesData[earIndex].location
    cdef Vector3 v3 = verticesData[nextIndex].location

    cdef Py_ssize_t i
    for i in range(polyLength):
        if i != previousIndex and i != earIndex and i != nextIndex and pointInsideTriangle(v1, v2, v3, verticesData[i].location):
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
cdef void projectPolygonVertices(Vector3DList vertices, Py_ssize_t polyStart, Py_ssize_t polyLength,
                                 unsigned int* oldIndices, Vertex* verticesData):
    # Compute polygon normal with Nowell's method.
    cdef Vector3 polyNormal = toVector3((0, 0, 0))
    cdef Py_ssize_t i
    for i in range(polyLength):
        v1 = vertices.data[oldIndices[polyStart + i]]
        v2 = vertices.data[oldIndices[polyStart + (i + 1) % polyLength]]

        polyNormal.x += (v1.y - v2.y) * (v1.z + v2.z)
        polyNormal.y += (v1.z - v2.z) * (v1.x + v2.x)
        polyNormal.z += (v1.x - v2.x) * (v1.y + v2.y)

        verticesData[i].index = oldIndices[polyStart + i]
        verticesData[i].location = v1
        verticesData[i].previous = (polyLength + i - 1) % polyLength
        verticesData[i].next = (i + 1) % polyLength

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
    cdef Vector3 vertex, cross, rotPolyVertex
    cdef float dot
    for i in range(polyLength):
        vertex = verticesData[i].location

        crossVec3(&cross, &rotAxis, &vertex)
        dot = dotVec3(&rotAxis, &vertex)

        rotPolyVertex.x = cost * vertex.x + sint * cross.x + dot * fact * rotAxis.x
        rotPolyVertex.y = cost * vertex.y + sint * cross.y + dot * fact * rotAxis.y
        rotPolyVertex.z = 0.0

        verticesData[i].location = rotPolyVertex
