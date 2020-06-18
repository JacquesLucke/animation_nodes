import cython
from libc.math cimport sin, cos
from cpython.mem cimport PyMem_Malloc, PyMem_Free
from ... data_structures cimport (
    Vector3DList, PolygonIndicesList)
from ... math cimport (
    Vector3, crossVec3, subVec3, dotVec3, toVector3, lengthVec3,
    angleNormalizedVec3, normalizeVec3_InPlace
)

cdef struct Vertex:
    Py_ssize_t index
    Vector3 location
    float angle
    bint isEar
    Py_ssize_t previous
    Py_ssize_t next

cdef struct VertexList:
    Py_ssize_t head
    Vertex *data

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

    cdef Vertex* polyVertices
    cdef VertexList vertexList
    cdef Py_ssize_t j, polyStart, triangleIndex, polyIndex, index, earIndex

    polyIndex = 0
    triangleIndex = 0
    for i in range(polygonAmount):
        polyStart = oldPolyStarts[i]
        polyLength = oldPolyLengths[i]

        # Initialization of polygon's vertices.
        vertexList.head = 0
        vertexList.data = <Vertex*>PyMem_Malloc(polyLength * sizeof(Vertex))

        polyVertices = vertexList.data
        for j in range(1, polyLength - 1):
            polyVertices[j].index = oldIndices[polyStart + j]
            polyVertices[j].location = vertices.data[oldIndices[polyStart + j]]
            polyVertices[j].previous = j - 1
            polyVertices[j].next = j + 1

        index = 0
        polyVertices[index].index = oldIndices[polyStart + index]
        polyVertices[index].location = vertices.data[oldIndices[polyStart + index]]
        polyVertices[index].previous = polyLength - 1
        polyVertices[index].next = 1

        index = polyLength - 1
        polyVertices[index].index = oldIndices[polyStart + index]
        polyVertices[index].location = vertices.data[oldIndices[polyStart + index]]
        polyVertices[index].previous = polyLength - 2
        polyVertices[index].next = 0

        # Project vertices in xy-plane.
        projectPolygonVertices(&vertexList)

        # Check polygon polarity.
        makeSurePolygonIsCounterClockwise(&vertexList)

        # Calculate angle and status of vertices.
        for j in range(polyLength):
            polyVertices[j].angle = calculateAngleWithSign(polyVertices, j)
            setVertexEarStatus(&vertexList, j)

        # Calculate triangle polygon indices.
        for j in range(polyLength - 3):
            # Removing an ear which has smallest inner-angle.
            earIndex = findEarHasMinAngle(&vertexList)

            newPolyStarts[triangleIndex] = polyIndex
            newPolyLengths[triangleIndex] = 3
            triangleIndex += 1

            newIndices[polyIndex] = polyVertices[polyVertices[earIndex].previous].index
            newIndices[polyIndex + 1] = polyVertices[earIndex].index
            newIndices[polyIndex + 2] = polyVertices[polyVertices[earIndex].next].index
            polyIndex += 3

            removeEarVertex(&vertexList, earIndex)

        earIndex = polyVertices[vertexList.head].next

        newPolyStarts[triangleIndex] = polyIndex
        newPolyLengths[triangleIndex] = 3
        triangleIndex += 1

        newIndices[polyIndex] = polyVertices[polyVertices[earIndex].previous].index
        newIndices[polyIndex + 1] = polyVertices[earIndex].index
        newIndices[polyIndex + 2] = polyVertices[polyVertices[earIndex].next].index
        polyIndex += 3

        PyMem_Free(polyVertices)

    return newPolygons

# Find the index of minimum angle.
cdef int findEarHasMinAngle(VertexList *vertexList):
    cdef Py_ssize_t headIndex = vertexList[0].head
    cdef Vertex* polyVertices = vertexList[0].data
    cdef Py_ssize_t currentIndex

    # The angleMin is set to 3.15 because a head-vertex may not be an ear but can have small angle.
    cdef float angleMin = 3.15
    cdef float angle
    cdef Py_ssize_t angleMinIndex = 0

    currentIndex = headIndex
    while True:
        if polyVertices[currentIndex].isEar:
            angle = abs(polyVertices[currentIndex].angle)
            if angleMin > angle:
                angleMin = angle
                angleMinIndex = currentIndex
        currentIndex = polyVertices[currentIndex].next
        if currentIndex == headIndex: break

    return angleMinIndex

# Remove ear-vertex and update neighbor-vertices.
cdef void removeEarVertex(VertexList *vertexList, Py_ssize_t earIndex):
    cdef Vertex* polyVertices = vertexList[0].data
    if earIndex == vertexList[0].head: vertexList[0].head = polyVertices[earIndex].next

    cdef Py_ssize_t previousIndex, nextIndex
    previousIndex = polyVertices[earIndex].previous
    nextIndex = polyVertices[earIndex].next

    polyVertices[nextIndex].previous = previousIndex
    polyVertices[previousIndex].next = nextIndex

    polyVertices[previousIndex].angle = calculateAngleWithSign(polyVertices, previousIndex)
    setVertexEarStatus(vertexList, previousIndex)
    polyVertices[nextIndex].angle = calculateAngleWithSign(polyVertices, nextIndex)
    setVertexEarStatus(vertexList, nextIndex)

# Make sure normal (+z) is correct. For counter-clockwise polygon has area <= 0.
@cython.cdivision(True)
cdef void makeSurePolygonIsCounterClockwise(VertexList *vertexList):
    cdef Py_ssize_t headIndex = vertexList[0].head
    cdef Vertex* polyVertices = vertexList[0].data
    cdef Py_ssize_t currentIndex

    cdef Vector3 v1, v2
    cdef float area = 0.0
    currentIndex = headIndex
    while(True):
        v1 = polyVertices[currentIndex].location
        currentIndex = polyVertices[currentIndex].next
        v2 = polyVertices[currentIndex].location
        area += (v2.x - v1.x) * (v2.y + v1.y)
        if currentIndex == headIndex: break

    if area > 0.0:
        currentIndex = headIndex
        while(True):
            previousIndex = polyVertices[currentIndex].previous
            nextIndex = polyVertices[currentIndex].next
            polyVertices[currentIndex].previous = nextIndex
            polyVertices[currentIndex].next = previousIndex
            currentIndex = nextIndex
            if currentIndex == headIndex: break

# Calculate inner angle.
cdef float calculateAngleWithSign(Vertex* polyVertices, Py_ssize_t index):
    cdef Vector3 v1 = polyVertices[polyVertices[index].previous].location
    cdef Vector3 v2 = polyVertices[index].location
    cdef Vector3 v3 = polyVertices[polyVertices[index].next].location
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

# Set the status of a vertex whether it is ear or not.
cdef void setVertexEarStatus(VertexList *vertexList, Py_ssize_t index):
    cdef Py_ssize_t headIndex = vertexList[0].head
    cdef Vertex* polyVertices = vertexList[0].data
    if polyVertices[index].angle >= 0.0 and not isAnyPointInsideTriangle(headIndex, polyVertices, index):
        polyVertices[index].isEar = True
    else:
        polyVertices[index].isEar = False

# Checking points (reflex type) lies inside the new triangle.
cdef bint isAnyPointInsideTriangle(Py_ssize_t headIndex, Vertex* polyVertices, Py_ssize_t earIndex):
    cdef Py_ssize_t previousIndex = polyVertices[earIndex].previous
    cdef Py_ssize_t nextIndex = polyVertices[earIndex].next

    cdef Vector3 v1 = polyVertices[previousIndex].location
    cdef Vector3 v2 = polyVertices[earIndex].location
    cdef Vector3 v3 = polyVertices[nextIndex].location

    cdef Py_ssize_t currentIndex = headIndex
    while True:
        if (currentIndex != previousIndex and currentIndex != earIndex and currentIndex != nextIndex and
            pointInsideTriangle(v1, v2, v3, polyVertices[currentIndex].location)): return True

        currentIndex = polyVertices[currentIndex].next
        if currentIndex == headIndex: break
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
cdef void projectPolygonVertices(VertexList *vertexList):
    cdef Py_ssize_t headIndex = vertexList[0].head
    cdef Vertex* polyVertices = vertexList[0].data
    cdef Py_ssize_t currentIndex

    # Compute polygon normal with Nowell's method.
    cdef Vector3 polyNormal = toVector3((0, 0, 0))
    currentIndex = headIndex
    while True:
        v1 = polyVertices[currentIndex].location
        currentIndex = polyVertices[currentIndex].next
        v2 = polyVertices[currentIndex].location

        polyNormal.x += (v1.y - v2.y) * (v1.z + v2.z)
        polyNormal.y += (v1.z - v2.z) * (v1.x + v2.x)
        polyNormal.z += (v1.x - v2.x) * (v1.y + v2.y)
        if currentIndex == headIndex: break

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
    currentIndex = headIndex
    while True:
        vertex = polyVertices[currentIndex].location

        crossVec3(&cross, &rotAxis, &vertex)
        dot = dotVec3(&rotAxis, &vertex)

        rotPolyVertex.x = cost * vertex.x + sint * cross.x + dot * fact * rotAxis.x
        rotPolyVertex.y = cost * vertex.y + sint * cross.y + dot * fact * rotAxis.y
        rotPolyVertex.z = 0.0

        polyVertices[currentIndex].location = rotPolyVertex
        currentIndex = polyVertices[currentIndex].next
        if currentIndex == headIndex: break
