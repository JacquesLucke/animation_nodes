import cython
from ... utils.limits cimport INT_MAX
from ... math cimport Vector3, toVector3
from ... data_structures cimport (
    Mesh,
    LongList,
    FloatList,
    Vector3DList,
    EdgeIndicesList,
    FalloffEvaluator,
    VirtualDoubleList,
    PolygonIndicesList,
)

def marchingSquaresOnGrid(long xDivisions, long yDivisions, float xSize, float ySize,
                          FalloffEvaluator falloffEvaluator, long amountThreshold,
                          VirtualDoubleList thresholds, offset, str distanceMode):

    cdef Vector3DList points = getGridPoints(xDivisions, yDivisions, xSize, ySize,
                                             toVector3(offset), distanceMode)
    cdef FloatList strengths = falloffEvaluator.evaluateList(points)

    cdef long nx = limitAmount(xDivisions), ny = limitAmount(yDivisions)
    cdef Py_ssize_t i, j, k, index, a, b, c, d
    cdef long _nx = nx - 1, _ny = ny - 1

    meshes = []
    for i in range(_ny):
        index = nx * i
        for j in range(_nx):
            # Clockwise order.
            a = nx + index + j
            b = a + 1
            d = j + index
            c = d + 1

            for k in range(amountThreshold):
                meshes.append(getMeshOfSquare(points, strengths, <float>thresholds.get(k),
                                              a, b, c, d))
    return Mesh.join(*meshes), points

def marchingSquaresOnMesh(Mesh mesh, FalloffEvaluator falloffEvaluator, long amountThreshold,
                          VirtualDoubleList thresholds):

    cdef Vector3DList points = mesh.vertices
    cdef PolygonIndicesList polygons = mesh.polygons
    cdef FloatList strengths = falloffEvaluator.evaluateList(points)

    cdef unsigned int *polyStarts = polygons.polyStarts.data
    cdef unsigned int *indices = polygons.indices.data
    cdef Py_ssize_t i, a, b, c, d, start
    cdef long indexSquare
    cdef float tolerance

    meshes = []
    for i in range(polygons.getLength()):
        start = polyStarts[i]
        a = indices[start]
        b = indices[start + 1]
        c = indices[start + 2]
        d = indices[start + 3]
        for j in range(amountThreshold):
            tolerance = <float>thresholds.get(j)
            indexSquare = binaryToDecimal(a, b, c, d, strengths, tolerance)
            if indexSquare == 0 or indexSquare == 15: continue
            meshes.append(getMeshOfSquare(points, strengths, tolerance,
                                          a, b, c, d, indexSquare))
    return Mesh.join(*meshes)

# http://jamie-wong.com/2014/08/19/metaballs-and-marching-squares/ is modified for multiple
# tolerance values, and works for grid as well as mesh surface.
def getMeshOfSquare(Vector3DList points, FloatList strengths, float tolerance,
                    Py_ssize_t a, Py_ssize_t b, Py_ssize_t c, Py_ssize_t d,
                    long indexSquare):
    '''
    Indices order for a square.
        a-------b
        '       '
        '       '
        '       '
        d-------c
    '''
    if indexSquare == 1:
        return getMeshSingle(d, c, d, a, points, strengths, tolerance)
    elif indexSquare == 2:
        return getMeshSingle(c, d, c, b, points, strengths, tolerance)
    elif indexSquare == 3:
        return getMeshSingle(c, b, d, a, points, strengths, tolerance)
    elif indexSquare == 4:
        return getMeshSingle(b, a, b, c, points, strengths, tolerance)
    elif indexSquare == 5:
        return getMeshDouble(b, c, d, c, b, a, d, a, points, strengths, tolerance)
    elif indexSquare == 6:
        return getMeshSingle(b, a, c, d, points, strengths, tolerance)
    elif indexSquare == 7:
        return getMeshSingle(b, a, d, a, points, strengths, tolerance)
    elif indexSquare == 8:
        return getMeshSingle(a, b, a, d, points, strengths, tolerance)
    elif indexSquare == 9:
        return getMeshSingle(a, b, d, c, points, strengths, tolerance)
    elif indexSquare == 10:
        return getMeshDouble(a, b, c, b, a, d, c, d, points, strengths, tolerance)
    elif indexSquare == 11:
        return getMeshSingle(a, b, c, b, points, strengths, tolerance)
    elif indexSquare == 12:
        return getMeshSingle(a, d, b, c, points, strengths, tolerance)
    elif indexSquare == 13:
        return getMeshSingle(b, c, d, c, points, strengths, tolerance)
    elif indexSquare == 14:
        return getMeshSingle(a, d, c, d, points, strengths, tolerance)

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

cdef Mesh getMeshSingle(Py_ssize_t a, Py_ssize_t b, Py_ssize_t c, Py_ssize_t d,
                        Vector3DList points, FloatList strengths, float tolerance):
    cdef Vector3DList vertices = Vector3DList(length = 2)
    cdef EdgeIndicesList edges = EdgeIndicesList(length = 1)
    cdef PolygonIndicesList polygons = PolygonIndicesList()

    edges.data[0].v1 = 0
    edges.data[0].v2 = 1

    lerpVec3(vertices.data + 0, points.data + a, points.data + b, strengths.data[a],
             strengths.data[b], tolerance)
    lerpVec3(vertices.data + 1, points.data + c, points.data + d, strengths.data[c],
             strengths.data[d], tolerance)
    return Mesh(vertices, edges, polygons)

cdef Mesh getMeshDouble(Py_ssize_t a1, Py_ssize_t b1, Py_ssize_t c1, Py_ssize_t d1,
                        Py_ssize_t a2, Py_ssize_t b2, Py_ssize_t c2, Py_ssize_t d2,
                        Vector3DList points, FloatList strengths, float tolerance):
    cdef Vector3DList vertices = Vector3DList(length = 4)
    cdef EdgeIndicesList edges = EdgeIndicesList(length = 2)
    cdef PolygonIndicesList polygons = PolygonIndicesList()

    edges.data[0].v1 = 0
    edges.data[0].v2 = 1

    lerpVec3(vertices.data + 0, points.data + a1, points.data + b1, strengths.data[a1],
             strengths.data[b1], tolerance)
    lerpVec3(vertices.data + 1, points.data + c1, points.data + d1, strengths.data[c1],
             strengths.data[d1], tolerance)

    edges.data[1].v1 = 2
    edges.data[1].v2 = 3

    lerpVec3(vertices.data + 2, points.data + a2, points.data + b2, strengths.data[a2],
             strengths.data[b2], tolerance)
    lerpVec3(vertices.data + 3, points.data + c2, points.data + d2, strengths.data[c2],
             strengths.data[d2], tolerance)
    return Mesh(vertices, edges, polygons)

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
