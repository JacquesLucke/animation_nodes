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

cdef struct Vertices:
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

    cdef Vertex* vertexData
    cdef Vertices verticesData
    cdef Py_ssize_t polyStart, triangleIndex, polyIndex
    cdef Py_ssize_t j, index, earIndex, headIndex, currentIndex

    polyIndex = 0
    triangleIndex = 0
    for i in range(polygonAmount):
        polyStart = oldPolyStarts[i]
        polyLength = oldPolyLengths[i]

        # Initialization of polygon's vertices.
        verticesData.head = 0
        verticesData.data = <Vertex*>PyMem_Malloc(polyLength * sizeof(Vertex))

        vertexData = verticesData.data
        for j in range(1, polyLength - 1):
            vertexData[j].index = oldIndices[polyStart + j]
            vertexData[j].location = vertices.data[oldIndices[polyStart + j]]
            vertexData[j].previous = j - 1
            vertexData[j].next = j + 1

        index = 0
        vertexData[index].index = oldIndices[polyStart + index]
        vertexData[index].location = vertices.data[oldIndices[polyStart + index]]
        vertexData[index].previous = polyLength - 1
        vertexData[index].next = 1

        index = polyLength - 1
        vertexData[index].index = oldIndices[polyStart + index]
        vertexData[index].location = vertices.data[oldIndices[polyStart + index]]
        vertexData[index].previous = polyLength - 2
        vertexData[index].next = 0

        # Project vertices in xy-plane.
        projectPolygonVertices(verticesData)

        # Check polygon polarity.
        makeSurePolygonIsCounterClockwise(verticesData)

        # Calculate angle and status of vertices.
        for j in range(polyLength):
            vertexData[j].angle = calculateAngleWithSign(vertexData, j)
            setVertexEarStatus(verticesData, j)

        # Calculate triangle polygon indices.
        for j in range(polyLength - 3):
            # Removing an ear which has smallest inner-angle.
            earIndex = findEarHasMinAngle(verticesData)

            newPolyStarts[triangleIndex] = polyIndex
            newPolyLengths[triangleIndex] = 3
            triangleIndex += 1

            newIndices[polyIndex] = vertexData[vertexData[earIndex].previous].index
            newIndices[polyIndex + 1] = vertexData[earIndex].index
            newIndices[polyIndex + 2] = vertexData[vertexData[earIndex].next].index
            polyIndex += 3

            if earIndex == verticesData.head: verticesData.head = vertexData[earIndex].next
            removeEarVertex(verticesData, earIndex)

        newPolyStarts[triangleIndex] = polyIndex
        newPolyLengths[triangleIndex] = 3
        triangleIndex += 1

        index = 0
        headIndex = verticesData.head
        currentIndex = headIndex
        while True:
            newIndices[polyIndex + index] = vertexData[currentIndex].index
            currentIndex = vertexData[currentIndex].next
            index += 1
            if currentIndex == headIndex: break
        polyIndex += 3

        PyMem_Free(vertexData)

    return newPolygons

# Find the index of minimum angle.
cdef int findEarHasMinAngle(Vertices verticesData):
    cdef Py_ssize_t headIndex = verticesData.head
    cdef Vertex* vertexData = verticesData.data
    cdef Py_ssize_t currentIndex

    # The angleMin is set to 3.15 because a head-vertex may not be an ear but can have small angle.
    cdef float angleMin = 3.15
    cdef float angle
    cdef Py_ssize_t angleMinIndex = 0

    currentIndex = headIndex
    while True:
        if vertexData[currentIndex].isEar:
            angle = abs(vertexData[currentIndex].angle)
            if angleMin > angle:
                angleMin = angle
                angleMinIndex = currentIndex
        currentIndex = vertexData[currentIndex].next
        if currentIndex == headIndex: break

    return angleMinIndex

# Remove ear-vertex and update neighbor-vertices.
cdef void removeEarVertex(Vertices verticesData, Py_ssize_t earIndex):
    cdef Vertex* vertexData = verticesData.data

    cdef Py_ssize_t previousIndex, nextIndex
    previousIndex = vertexData[earIndex].previous
    nextIndex = vertexData[earIndex].next

    vertexData[nextIndex].previous = previousIndex
    vertexData[previousIndex].next = nextIndex

    vertexData[previousIndex].angle = calculateAngleWithSign(vertexData, previousIndex)
    setVertexEarStatus(verticesData, previousIndex)
    vertexData[nextIndex].angle = calculateAngleWithSign(vertexData, nextIndex)
    setVertexEarStatus(verticesData, nextIndex)

# Make sure normal (+z) is correct. For counter-clockwise polygon has area <= 0.
@cython.cdivision(True)
cdef void makeSurePolygonIsCounterClockwise(Vertices verticesData):
    cdef Py_ssize_t headIndex = verticesData.head
    cdef Vertex* vertexData = verticesData.data
    cdef Py_ssize_t currentIndex

    cdef Vector3 v1, v2
    cdef float area = 0.0
    currentIndex = headIndex
    while(True):
        v1 = vertexData[currentIndex].location
        currentIndex = vertexData[currentIndex].next
        v2 = vertexData[currentIndex].location
        area += (v2.x - v1.x) * (v2.y + v1.y)
        if currentIndex == headIndex: break

    if area > 0.0:
        currentIndex = headIndex
        while(True):
            previousIndex = vertexData[currentIndex].previous
            nextIndex = vertexData[currentIndex].next
            vertexData[currentIndex].previous = nextIndex
            vertexData[currentIndex].next = previousIndex
            currentIndex = nextIndex
            if currentIndex == headIndex: break

# Calculate inner angle.
cdef float calculateAngleWithSign(Vertex* vertexData, Py_ssize_t index):
    cdef Vector3 v1 = vertexData[vertexData[index].previous].location
    cdef Vector3 v2 = vertexData[index].location
    cdef Vector3 v3 = vertexData[vertexData[index].next].location
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
cdef void setVertexEarStatus(Vertices verticesData, Py_ssize_t index):
    cdef Py_ssize_t headIndex = verticesData.head
    cdef Vertex* vertexData = verticesData.data
    if vertexData[index].angle >= 0.0 and not isAnyPointInsideTriangle(headIndex, vertexData, index):
        vertexData[index].isEar = True
    else:
        vertexData[index].isEar = False

# Checking points (reflex type) lies inside the new triangle.
cdef bint isAnyPointInsideTriangle(Py_ssize_t headIndex, Vertex* vertexData, Py_ssize_t earIndex):
    cdef Py_ssize_t previousIndex = vertexData[earIndex].previous
    cdef Py_ssize_t nextIndex = vertexData[earIndex].next

    cdef Vector3 v1 = vertexData[previousIndex].location
    cdef Vector3 v2 = vertexData[earIndex].location
    cdef Vector3 v3 = vertexData[nextIndex].location

    cdef Py_ssize_t currentIndex = headIndex
    while True:
        if (currentIndex != previousIndex and currentIndex != earIndex and currentIndex != nextIndex and
            pointInsideTriangle(v1, v2, v3, vertexData[currentIndex].location)): return True

        currentIndex = vertexData[currentIndex].next
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
cdef void projectPolygonVertices(Vertices verticesData):
    cdef Py_ssize_t headIndex = verticesData.head
    cdef Vertex* vertexData = verticesData.data
    cdef Py_ssize_t currentIndex

    # Compute polygon normal with Nowell's method.
    cdef Vector3 polyNormal = toVector3((0, 0, 0))
    currentIndex = headIndex
    while True:
        v1 = vertexData[currentIndex].location
        currentIndex = vertexData[currentIndex].next
        v2 = vertexData[currentIndex].location

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
        vertex = vertexData[currentIndex].location

        crossVec3(&cross, &rotAxis, &vertex)
        dot = dotVec3(&rotAxis, &vertex)

        rotPolyVertex.x = cost * vertex.x + sint * cross.x + dot * fact * rotAxis.x
        rotPolyVertex.y = cost * vertex.y + sint * cross.y + dot * fact * rotAxis.y
        rotPolyVertex.z = 0.0

        vertexData[currentIndex].location = rotPolyVertex
        currentIndex = vertexData[currentIndex].next
        if currentIndex == headIndex: break
