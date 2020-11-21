import cython
from ... utils.limits cimport INT_MAX
from cpython.mem cimport PyMem_Malloc, PyMem_Free
from ... math cimport Vector3, toVector3, normalizeVec3_InPlace
from ... data_structures cimport (
    Mesh,
    FloatList,
    Vector3DList,
    EdgeIndicesList,
    FalloffEvaluator,
    VirtualDoubleList,
    PolygonIndicesList,
)

cdef struct Vertex:
    Vector3 location
    Vector3 normal

cdef struct VertexList:
    Py_ssize_t vertexAmount
    Vertex *data


cdef struct Edge:
    Py_ssize_t start
    Py_ssize_t end

cdef struct EdgeList:
    Py_ssize_t edgeAmount
    Edge *data


cdef struct EdgePrevious:
    Py_ssize_t start
    Py_ssize_t end
    Py_ssize_t vertexIndex

cdef struct EdgePreviousList:
    Py_ssize_t edgePreviousAmount
    EdgePrevious *data


def marchingSquaresOnGrid(long xDivisions, long yDivisions, float xSize, float ySize,
                          FalloffEvaluator falloffEvaluator, long amountThreshold,
                          VirtualDoubleList thresholds, offset, str distanceMode):

    cdef long nx = limitAmount(xDivisions), ny = limitAmount(yDivisions)
    cdef long _nx = nx - 1, _ny = ny - 1
    cdef long squareAmount = _nx * _ny

    # Initialization of vertices of contour.
    cdef Vertex* vertices
    cdef VertexList vertexList

    vertexList.vertexAmount = 0
    vertexList.data = <Vertex*>PyMem_Malloc(4 * squareAmount * sizeof(Vertex))
    vertices = vertexList.data

    # Initialization of edges contour.
    cdef Edge* edges
    cdef EdgeList edgeList

    edgeList.edgeAmount = 0
    edgeList.data = <Edge*>PyMem_Malloc(2 * squareAmount * sizeof(Edge))
    edges = edgeList.data

    # Initialization of edgesPrevious.
    cdef EdgePrevious* edgesPrevious
    cdef EdgePreviousList edgePreviousList

    edgePreviousList.edgePreviousAmount = 0
    edgePreviousList.data = <EdgePrevious*>PyMem_Malloc(4 * squareAmount * sizeof(EdgePrevious))
    edgesPrevious = edgePreviousList.data

    cdef Py_ssize_t i
    for i in range(2 * squareAmount):
        edgesPrevious[i].start = -1
        edgesPrevious[i].end = -1

    cdef Vector3DList points = getGridPoints(xDivisions, yDivisions, xSize, ySize,
                                             toVector3(offset), distanceMode)
    cdef FloatList strengths = falloffEvaluator.evaluateList(points)
    cdef Py_ssize_t j, k, index, a, b, c, d
    cdef Vector3 polyNormal

    polyNormal.x = 0
    polyNormal.y = 0
    polyNormal.z = 0

    for i in range(_ny):
        index = nx * i
        for j in range(_nx):
            # Clockwise order.
            a = nx + index + j
            b = a + 1
            d = j + index
            c = d + 1

            for k in range(amountThreshold):
                marchingSquare(points, strengths, <float>thresholds.get(k), a, b, c, d,
                               &vertexList, &edgeList, &edgePreviousList, polyNormal)

    cdef Py_ssize_t vertexAmount = vertexList.vertexAmount
    cdef Vector3DList verticesOut = Vector3DList(length = vertexAmount)
    for i in range(vertexAmount):
        verticesOut.data[i] = vertices[i].location

    cdef Py_ssize_t edgeAmount = edgeList.edgeAmount
    cdef EdgeIndicesList edgesOut = EdgeIndicesList(length = edgeAmount)
    for i in range(edgeAmount):
       edgesOut.data[i].v1 = edges[i].start
       edgesOut.data[i].v2 = edges[i].end

    cdef PolygonIndicesList polygonsOut = PolygonIndicesList()

    PyMem_Free(vertices)
    PyMem_Free(edges)
    PyMem_Free(edgesPrevious)
    return Mesh(verticesOut, edgesOut, polygonsOut), points


def marchingSquaresOnMesh(Vector3DList points, PolygonIndicesList polygons, Vector3DList polyNormals,
                          FalloffEvaluator falloffEvaluator, long amountThreshold, VirtualDoubleList thresholds):

    cdef long polyAmount = polygons.getLength()

    # Initialization of vertices of contour.
    cdef Vertex* vertices
    cdef VertexList vertexList

    vertexList.vertexAmount = 0
    vertexList.data = <Vertex*>PyMem_Malloc(4 * polyAmount * sizeof(Vertex))
    vertices = vertexList.data

    # Initialization of edges contour.
    cdef Edge* edges
    cdef EdgeList edgeList

    edgeList.edgeAmount = 0
    edgeList.data = <Edge*>PyMem_Malloc(2 * polyAmount * sizeof(Edge))
    edges = edgeList.data

    # Initialization of edgesPrevious.
    cdef EdgePrevious* edgesPrevious
    cdef EdgePreviousList edgePreviousList

    edgePreviousList.edgePreviousAmount = 0
    edgePreviousList.data = <EdgePrevious*>PyMem_Malloc(4 * polyAmount * sizeof(EdgePrevious))
    edgesPrevious = edgePreviousList.data

    cdef Py_ssize_t i
    for i in range(2 * polyAmount):
        edgesPrevious[i].start = -1
        edgesPrevious[i].end = -1

    cdef FloatList strengths = falloffEvaluator.evaluateList(points)
    cdef unsigned int *polyStarts = polygons.polyStarts.data
    cdef unsigned int *indices = polygons.indices.data
    cdef Py_ssize_t a, b, c, d, start
    cdef Vector3 polyNormal

    for i in range(polygons.getLength()):
        start = polyStarts[i]
        a = indices[start]
        b = indices[start + 1]
        c = indices[start + 2]
        d = indices[start + 3]
        polyNormal = polyNormals.data[i]
        normalizeVec3_InPlace(&polyNormal)
        for j in range(amountThreshold):
            marchingSquare(points, strengths, <float>thresholds.get(j), a, b, c, d,
                           &vertexList, &edgeList, &edgePreviousList, polyNormal)


    cdef Py_ssize_t vertexAmount = vertexList.vertexAmount
    cdef Vector3DList verticesOut = Vector3DList(length = vertexAmount)
    cdef Vector3DList normalsOut = Vector3DList(length = vertexAmount)
    for i in range(vertexAmount):
        verticesOut.data[i] = vertices[i].location
        normalsOut.data[i] = vertices[i].normal

    cdef Py_ssize_t edgeAmount = edgeList.edgeAmount
    cdef EdgeIndicesList edgesOut = EdgeIndicesList(length = edgeAmount)
    for i in range(edgeAmount):
       edgesOut.data[i].v1 = edges[i].start
       edgesOut.data[i].v2 = edges[i].end

    cdef PolygonIndicesList polygonsOut = PolygonIndicesList()

    PyMem_Free(vertices)
    PyMem_Free(edges)
    PyMem_Free(edgesPrevious)
    return Mesh(verticesOut, edgesOut, polygonsOut), normalsOut


# http://jamie-wong.com/2014/08/19/metaballs-and-marching-squares/ is modified for multiple
# tolerance values, and works for grid as well as mesh surface.
cdef marchingSquare(Vector3DList points, FloatList strengths, float tolerance, Py_ssize_t a,
                     Py_ssize_t b, Py_ssize_t c, Py_ssize_t d, VertexList* vertexList,
                     EdgeList* edgeList, EdgePreviousList* edgePreviousList, Vector3 polyNormal):
    '''
    Indices order for a square.
        a-------b
        '       '
        '       '
        '       '
        d-------c
    '''
    cdef long indexSquare = binaryToDecimal(a, b, c, d, strengths, tolerance)
    if indexSquare == 0 or indexSquare == 15:
        return
    elif indexSquare == 1:
        calculateContourSegment(d, c, d, a, points, strengths, tolerance, vertexList,
                                edgeList, edgePreviousList, polyNormal)
    elif indexSquare == 2:
        calculateContourSegment(c, d, c, b, points, strengths, tolerance, vertexList,
                                edgeList, edgePreviousList, polyNormal)
    elif indexSquare == 3:
        calculateContourSegment(c, b, d, a, points, strengths, tolerance, vertexList,
                                edgeList, edgePreviousList, polyNormal)
    elif indexSquare == 4:
        calculateContourSegment(b, a, b, c, points, strengths, tolerance, vertexList,
                                edgeList, edgePreviousList, polyNormal)
    elif indexSquare == 5:
        calculateContourSegment(b, c, d, c, points, strengths, tolerance, vertexList,
                                edgeList, edgePreviousList, polyNormal)
        calculateContourSegment(b, a, d, a, points, strengths, tolerance, vertexList,
                                edgeList, edgePreviousList, polyNormal)
    elif indexSquare == 6:
        calculateContourSegment(b, a, c, d, points, strengths, tolerance, vertexList,
                                edgeList, edgePreviousList, polyNormal)
    elif indexSquare == 7:
        calculateContourSegment(b, a, d, a, points, strengths, tolerance, vertexList,
                                edgeList, edgePreviousList, polyNormal)
    elif indexSquare == 8:
        calculateContourSegment(a, b, a, d, points, strengths, tolerance, vertexList,
                                edgeList, edgePreviousList, polyNormal)
    elif indexSquare == 9:
        calculateContourSegment(a, b, d, c, points, strengths, tolerance, vertexList,
                                edgeList, edgePreviousList, polyNormal)
    elif indexSquare == 10:
        calculateContourSegment(a, b, c, b, points, strengths, tolerance, vertexList,
                                edgeList, edgePreviousList, polyNormal)
        calculateContourSegment(a, d, c, d, points, strengths, tolerance, vertexList,
                                edgeList, edgePreviousList, polyNormal)
    elif indexSquare == 11:
        calculateContourSegment(a, b, c, b, points, strengths, tolerance, vertexList,
                                edgeList, edgePreviousList, polyNormal)
    elif indexSquare == 12:
        calculateContourSegment(a, d, b, c, points, strengths, tolerance, vertexList,
                                edgeList, edgePreviousList, polyNormal)
    elif indexSquare == 13:
        calculateContourSegment(b, c, d, c, points, strengths, tolerance, vertexList,
                                edgeList, edgePreviousList, polyNormal)
    elif indexSquare == 14:
        calculateContourSegment(a, d, c, d, points, strengths, tolerance, vertexList,
                                edgeList, edgePreviousList, polyNormal)


cdef long binaryToDecimal(Py_ssize_t a, Py_ssize_t b, Py_ssize_t c, Py_ssize_t d,
                          FloatList strengths, float t):
    cdef float sa, sb, sc, sd
    sa, sb, sc, sd = strengths.data[a], strengths.data[b], strengths.data[c], strengths.data[d]

    # Binary order (sd, sc, sb, sa).
    if sa <= t: sa = 0
    else: sa = 1

    if sb <= t: sb = 0
    else: sb = 1

    if sc <= t: sc = 0
    else: sc = 1

    if sd <= t: sd = 0
    else: sd = 1

    return <long>(8.0 * sa + 4.0 * sb + 2.0 * sc + sd)


cdef void calculateContourSegment(Py_ssize_t a, Py_ssize_t b, Py_ssize_t c, Py_ssize_t d,
                                  Vector3DList points, FloatList strengths, float tolerance,
                                  VertexList* vertexList, EdgeList* edgeList,
                                  EdgePreviousList* edgePreviousList, Vector3 polyNormal):
    cdef Py_ssize_t start, end
    start = calculateVertexUpdateEdgePreviousList(a, b, points, strengths, tolerance,
                                                  vertexList, edgePreviousList, polyNormal)
    end = calculateVertexUpdateEdgePreviousList(c, d, points, strengths, tolerance,
                                                vertexList, edgePreviousList, polyNormal)
    if start == end: return
    cdef Py_ssize_t edgeAmount = edgeList[0].edgeAmount
    cdef Edge* edges = edgeList[0].data
    cdef Py_ssize_t i, startExist, endExist
    for i in range(edgeAmount):
        startExist = edges[i].start
        endExist = edges[i].end
        if start == startExist and end == endExist:
            return
        if start == endExist and end == startExist:
            return

    edges[edgeAmount].start = start
    edges[edgeAmount].end = end
    edgeList[0].edgeAmount += 1


cdef Py_ssize_t calculateVertexUpdateEdgePreviousList(Py_ssize_t a, Py_ssize_t b,
                                                      Vector3DList points, FloatList strengths,
                                                      float tolerance, VertexList* vertexList,
                                                      EdgePreviousList* edgePreviousList,
                                                      Vector3 polyNormal):
    cdef Py_ssize_t vertexAmount = vertexList[0].vertexAmount
    cdef Vertex* vertices = vertexList[0].data

    cdef Py_ssize_t edgePreviousAmount = edgePreviousList[0].edgePreviousAmount
    cdef EdgePrevious* edgesPrevious = edgePreviousList[0].data
    cdef Py_ssize_t i, start, end, vertexIndex

    vertexIndex = -1
    for i in range(edgePreviousAmount):
        start = edgesPrevious[i].start
        end = edgesPrevious[i].end
        if a == start and b == end:
            vertexIndex = edgesPrevious[i].vertexIndex
            break
        elif a == end and b == start:
            vertexIndex = edgesPrevious[i].vertexIndex
            break

    cdef Vector3 v
    if vertexIndex == -1:
        lerpVec3(&v, points.data + a, points.data + b, strengths.data[a], strengths.data[b],
                 tolerance)
        vertexIndex = vertexAmount
        vertices[vertexAmount].location = v
        vertices[vertexAmount].normal = polyNormal
        vertexList[0].vertexAmount += 1

    edgesPrevious[edgePreviousAmount].vertexIndex = vertexIndex
    edgesPrevious[edgePreviousAmount].start = a
    edgesPrevious[edgePreviousAmount].end = b
    edgePreviousList[0].edgePreviousAmount += 1

    return vertexIndex


cdef void lerpVec3(Vector3* target, Vector3* va, Vector3* vb, float a, float b, float tolerance):
    target.x = lerp(va.x, vb.x, a, b, tolerance)
    target.y = lerp(va.y, vb.y, a, b, tolerance)
    target.z = lerp(va.z, vb.z, a, b, tolerance)


@cython.cdivision(True)
cdef float lerp(float t1, float t2, float f1, float f2, float tolerance):
    return t1 + (tolerance - f1) * (t2 - t1) / (f2 - f1)


@cython.cdivision(True)
cdef Vector3DList getGridPoints(long xDivisions, long yDivisions, float size1,
                                float size2, Vector3 offset, str distanceMode):
    cdef:
        int xDiv = limitAmount(xDivisions)
        int yDiv = limitAmount(yDivisions)
        double xOffset, yOffset
        double xDis, yDis
        long x, y, index
        Vector3 vector
        Vector3DList points = Vector3DList(length = xDiv * yDiv)

    if distanceMode == "STEP":
        xDis, yDis = size1, size2
    elif distanceMode == "SIZE":
        xDis = size1 / max(xDiv - 1, 1)
        yDis = size2 / max(yDiv - 1, 1)

    xOffset = xDis * (xDiv - 1) / 2
    yOffset = yDis * (yDiv - 1) / 2

    for x in range(xDiv):
        for y in range(yDiv):
            index = y * xDiv + x
            vector.x = <float>(x * xDis - xOffset) + offset.x
            vector.y = <float>(y * yDis - yOffset) + offset.y
            vector.z =  offset.z
            points.data[index] = vector

    return points

cdef int limitAmount(n):
    return max(min(n, INT_MAX), 0)
