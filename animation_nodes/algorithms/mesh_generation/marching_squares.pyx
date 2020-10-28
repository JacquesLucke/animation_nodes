import cython
from ... utils.limits cimport INT_MAX
from ... math cimport Vector3, toVector3
from ... data_structures cimport (
    Mesh,
    FloatList,
    Vector3DList,
    EdgeIndicesList,
    FalloffEvaluator,
    VirtualDoubleList,
    PolygonIndicesList,
)

def marchingSquares(long xDivisions, long yDivisions, float xSize, float ySize, FalloffEvaluator falloffEvaluator,
                    long amountThreshold, VirtualDoubleList thresholds, offset, str distanceMode):

    cdef double xDis, yDis
    cdef Vector3DList points
    points, xDis, yDis = getGridPoints(xDivisions, yDivisions, xSize, ySize, toVector3(offset), distanceMode)

    cdef FloatList strengths = falloffEvaluator.evaluateList(points)
    cdef long nx = limitAmount(xDivisions), ny = limitAmount(yDivisions)
    cdef double _xDis = xDis / 2.0, _yDis = yDis / 2.0
    cdef Py_ssize_t i, j, k, index, ia, ib, ic, id
    cdef long _nx = nx - 1, _ny = ny - 1

    meshes = []
    for i in range(_ny):
        index = nx * i
        for j in range(_nx):
            # Counter-Clockwise
            ia = nx + index + j
            ib = ia + 1
            id = j + index
            ic = id + 1

            for k in range(amountThreshold):
                meshes.append(getMeshOfSquare(points, strengths, <float>thresholds.get(k),
                                              _xDis, _yDis, ia, ib, ic, id))

    return Mesh.join(*meshes), points

# http://jamie-wong.com/2014/08/19/metaballs-and-marching-squares/ is modified for multiple
# tolerance values.
def getMeshOfSquare(Vector3DList points, FloatList strengths, float tolerance, double _xDis,
                    double _yDis, Py_ssize_t ia, Py_ssize_t ib, Py_ssize_t ic, Py_ssize_t id):
    cdef float a, b, c, d
    a, b, c, d = strengths.data[ia], strengths.data[ib], strengths.data[ic], strengths.data[id]

    cdef Vector3 va, vb, vc, vd, v1, v2
    va, vb, vc, vd = points.data[ia], points.data[ib], points.data[ic], points.data[id]

    cdef Vector3DList vertices = Vector3DList(length = 2)
    cdef EdgeIndicesList edges = EdgeIndicesList(length = 1)
    cdef PolygonIndicesList polygons = PolygonIndicesList()

    cdef long indexSquare = binaryToDecimal(tolerance, a, b, c, d)
    v1.z = va.z
    v2.z = va.z
    if indexSquare == 0:
        return Mesh()
    elif indexSquare == 1:
        edges.data[0].v1 = 0
        edges.data[0].v2 = 1

        v1.x = lerp(tolerance, vd.x, vc.x, d, c)
        v1.y = vc.y
        v2.x = vd.x
        v2.y = lerp(tolerance, vd.y, va.y, d, a)
        vertices.data[0] = v1
        vertices.data[1] = v2
        return Mesh(vertices, edges, polygons)
    elif indexSquare == 2:
        edges.data[0].v1 = 0
        edges.data[0].v2 = 1

        v1.x = lerp(tolerance, vc.x, vd.x, c, d)
        v1.y = vc.y
        v2.x = vc.x
        v2.y = lerp(tolerance, vc.y, vb.y, c, b)
        vertices.data[0] = v1
        vertices.data[1] = v2
        return Mesh(vertices, edges, polygons)
    elif indexSquare == 3:
        edges.data[0].v1 = 0
        edges.data[0].v2 = 1

        v1.x = vc.x
        v1.y = lerp(tolerance, vc.y, vb.y, c, b)
        v2.x = vd.x
        v2.y = lerp(tolerance, vd.y, va.y, d, a)
        vertices.data[0] = v1
        vertices.data[1] = v2
        return Mesh(vertices, edges, polygons)
    elif indexSquare == 4:
        edges.data[0].v1 = 0
        edges.data[0].v2 = 1

        v1.x = lerp(tolerance, vb.x, va.x, b, a)
        v1.y = vb.y
        v2.x = vb.x
        v2.y = lerp(tolerance, vb.y, vc.y, b, c)
        vertices.data[0] = v1
        vertices.data[1] = v2
        return Mesh(vertices, edges, polygons)
    elif indexSquare == 5:
        edges.data[0].v1 = 0
        edges.data[0].v2 = 1

        v1.x = vb.x
        v1.y = lerp(tolerance, vb.y, vc.y, b, c)
        v2.x = lerp(tolerance, vd.x, vc.x, d, c)
        v2.y = vd.y
        vertices.data[0] = v1
        vertices.data[1] = v2

        edges.append((2,3))

        v1.x = lerp(tolerance, vb.x, va.x, b, a)
        v1.y = vb.y
        v2.x = vd.x
        v2.y = lerp(tolerance, vd.y, va.y, d, a)
        vertices.append_LowLevel(v1)
        vertices.append_LowLevel(v2)
        return Mesh(vertices, edges, polygons)
    elif indexSquare == 6:
        edges.data[0].v1 = 0
        edges.data[0].v2 = 1

        v1.x = lerp(tolerance, vb.x, va.x, b, a)
        v1.y = vb.y
        v2.x = lerp(tolerance, vc.x, vd.x, c, d)
        v2.y = vc.y
        vertices.data[0] = v1
        vertices.data[1] = v2
        return Mesh(vertices, edges, polygons)
    elif indexSquare == 7:
        edges.data[0].v1 = 0
        edges.data[0].v2 = 1

        v1.x = lerp(tolerance, vb.x, va.x, b, a)
        v1.y = vb.y
        v2.x = vd.x
        v2.y = lerp(tolerance, vd.y, va.y, d, a)
        vertices.data[0] = v1
        vertices.data[1] = v2
        return Mesh(vertices, edges, polygons)
    elif indexSquare == 8:
        edges.data[0].v1 = 0
        edges.data[0].v2 = 1

        v1.x = lerp(tolerance, va.x, vb.x, a, b)
        v1.y = va.y
        v2.x = va.x
        v2.y = lerp(tolerance, va.y, vd.y, a, d)
        vertices.data[0] = v1
        vertices.data[1] = v2
        return Mesh(vertices, edges, polygons)
    elif indexSquare == 9:
        edges.data[0].v1 = 0
        edges.data[0].v2 = 1

        v1.x = lerp(tolerance, va.x, vb.x, a, b)
        v1.y = va.y
        v2.x = lerp(tolerance, vd.x, vc.x, d, c)
        v2.y = vd.y
        vertices.data[0] = v1
        vertices.data[1] = v2
        return Mesh(vertices, edges, polygons)
    elif indexSquare == 10:
        edges.data[0].v1 = 0
        edges.data[0].v2 = 1

        v1.x = lerp(tolerance, va.x, vb.x, a, b)
        v1.y = va.y
        v2.x = vc.x
        v2.y = lerp(tolerance, vc.y, vb.y, c, b)
        vertices.data[0] = v1
        vertices.data[1] = v2

        edges.append((2,3))

        v1.x = va.x
        v1.y = lerp(tolerance, va.y, vd.y, a, d)
        v2.x = lerp(tolerance, vc.x, vd.x, c, d)
        v2.y = vc.y
        vertices.append_LowLevel(v1)
        vertices.append_LowLevel(v2)
        return Mesh(vertices, edges, polygons)
    elif indexSquare == 11:
        edges.data[0].v1 = 0
        edges.data[0].v2 = 1

        v1.x = lerp(tolerance, va.x, vb.x, a, b)
        v1.y = va.y
        v2.x = vc.x
        v2.y = lerp(tolerance, vc.y, vb.y, c, b)
        vertices.data[0] = v1
        vertices.data[1] = v2
        return Mesh(vertices, edges, polygons)
    elif indexSquare == 12:
        edges.data[0].v1 = 0
        edges.data[0].v2 = 1

        v1.x = va.x
        v1.y = lerp(tolerance, va.y, vd.y, a, d)
        v2.x = vb.x
        v2.y = lerp(tolerance, vb.y, vc.y, b, c)
        vertices.data[0] = v1
        vertices.data[1] = v2
        return Mesh(vertices, edges, polygons)
    elif indexSquare == 13:
        edges.data[0].v1 = 0
        edges.data[0].v2 = 1

        v1.x = vb.x
        v1.y = lerp(tolerance, vb.y, vc.y, b, c)
        v2.x = lerp(tolerance, vd.x, vc.x, d, c)
        v2.y = vd.y
        vertices.data[0] = v1
        vertices.data[1] = v2
        return Mesh(vertices, edges, polygons)
    elif indexSquare == 14:
        edges.data[0].v1 = 0
        edges.data[0].v2 = 1

        v1.x = va.x
        v1.y = lerp(tolerance, va.y, vd.y, a, d)
        v2.x = lerp(tolerance, vc.x, vd.x, c, d)
        v2.y = vc.y
        vertices.data[0] = v1
        vertices.data[1] = v2
        return Mesh(vertices, edges, polygons)
    elif indexSquare == 15:
        return Mesh()

cdef long binaryToDecimal(float t, float a, float b, float c, float d):
    # binary order (d, c, b, a)
    if a <= t: a = 0
    else: a = 1

    if b <= t: b = 0
    else: b = 1

    if c <= t: c = 0
    else: c = 1

    if d <= t: d = 0
    else: d = 1

    return <long>(8.0 * a + 4.0 * b + 2.0 * c + d)

@cython.cdivision(True)
cdef float lerp(float tolerance, float t1, float t2, float f1, float f2):
    return t1 + (tolerance - f1) * (t2 - t1) / (f2 - f1)

@cython.cdivision(True)
cdef getGridPoints(long xDivisions, long yDivisions, float size1, float size2,
                   Vector3 offset, str distanceMode):
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

    return points, xDis, yDis

cdef int limitAmount(n):
    return max(min(n, INT_MAX), 0)
