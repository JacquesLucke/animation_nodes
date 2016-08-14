from ... data_structures cimport Vector3DList, EdgeIndicesList, PolygonIndicesList

# Vertices
############################################

def vertices(float length, float width, int xDivisions, int yDivisions, offset = (0, 0, 0)):
    assert xDivisions >= 2
    assert yDivisions >= 2
    cdef:
        float xStep = length / <float>(xDivisions - 1)
        float yStep = width / <float>(yDivisions - 1)
        float xOffset, yOffset, zOffset
        int x, y

    vertices = Vector3DList(length = xDivisions * yDivisions)
    xOffset, yOffset, zOffset = offset
    cdef int tmp
    for x in range(xDivisions):
        tmp = x * yDivisions
        for y in range(yDivisions):
            vertices.base.data[(tmp + y) * 3 + 0] = x * xStep + xOffset
            vertices.base.data[(tmp + y) * 3 + 1] = y * yStep + yOffset
            vertices.base.data[(tmp + y) * 3 + 2] = zOffset
    return vertices


# Edges
############################################

def quadEdges(xDivisions, yDivisions, joinHorizontal = False, joinVertical = False):
    edges = EdgeIndicesList()
    edges.extend(innerQuadEdges(xDivisions, yDivisions))
    if joinHorizontal:
        edges.extend(joinHorizontalEdgesQuadEdges(xDivisions, yDivisions))
    if joinVertical:
        edges.extend(joinVerticalEdgesQuadEdges(xDivisions, yDivisions))
    return edges

def innerQuadEdges(long xDivisions, long yDivisions):
    assert xDivisions >= 2
    assert yDivisions >= 2

    cdef EdgeIndicesList edges = EdgeIndicesList(
            length = 2 * xDivisions * yDivisions - xDivisions - yDivisions)

    cdef long offset = 0
    cdef long i, j
    for i in range(xDivisions):
        for j in range(yDivisions - 1):
            edges.base.data[offset + 0] = i * yDivisions + j
            edges.base.data[offset + 1] = i * yDivisions + j + 1
            offset += 2
    for i in range(yDivisions):
        for j in range(xDivisions - 1):
            edges.base.data[offset + 0] = j * yDivisions + i
            edges.base.data[offset + 1] = j * yDivisions + i + yDivisions
            offset += 2
    return edges

def joinHorizontalEdgesQuadEdges(long xDivisions, long yDivisions):
    cdef EdgeIndicesList edges = EdgeIndicesList()
    cdef long i, offset = (xDivisions - 1) * yDivisions
    for i in range(yDivisions):
        print(i, i + offset)
        edges.append((i, i + offset))
    return edges

def joinVerticalEdgesQuadEdges(long xDivisions, long yDivisions):
    cdef EdgeIndicesList edges = EdgeIndicesList()
    cdef long i
    for i in range(xDivisions):
        edges.append((i * yDivisions, (i + 1) * yDivisions - 1))
    return edges


# Polygons
############################################


def quadPolygons(xDivisions, yDivisions, joinHorizontal = False, joinVertical = False):
    polygons = PolygonIndicesList()
    polygons.extend(innerQuadPolygons(xDivisions, yDivisions))
    if joinHorizontal:
        polygons.extend(joinHorizontalEdgesQuadPolygons(xDivisions, yDivisions))
    if joinVertical:
        polygons.extend(joinVerticalEdgesQuadPolygons(xDivisions, yDivisions))
    if joinHorizontal and joinVertical:
        polygons.append(joinCornersWithQuad(xDivisions, yDivisions))
    return polygons

def innerQuadPolygons(long xDivisions, long yDivisions):
    cdef long polyAmount = (xDivisions - 1) * (yDivisions - 1)
    polygons = PolygonIndicesList(
                    indicesAmount = 4 * polyAmount,
                    loopAmount = polyAmount)

    cdef long i, j, offset = 0
    for i in range(yDivisions - 1):
        for j in range(xDivisions - 1):
            polygons.polyStarts.data[offset / 4] = offset
            polygons.polyLengths.data[offset / 4] = 4
            polygons.indices.data[offset + 0] = (j + 1) * yDivisions + i
            polygons.indices.data[offset + 1] = (j + 1) * yDivisions + i + 1
            polygons.indices.data[offset + 2] = (j + 0) * yDivisions + i + 1
            polygons.indices.data[offset + 3] = (j + 0) * yDivisions + i
            offset += 4
    return polygons

def joinHorizontalEdgesQuadPolygons(xDivisions, yDivisions):
    polygons = PolygonIndicesList()
    offset = yDivisions * (xDivisions - 1)
    for i in range(yDivisions - 1):
        polygons.append((i + 1, i + offset + 1, i + offset, i))
    return polygons

def joinVerticalEdgesQuadPolygons(xDivisions, yDivisions):
    polygons = PolygonIndicesList()
    for i in range(0, (xDivisions - 1) * yDivisions, yDivisions):
        polygons.append((i + yDivisions - 1, i + 2 * yDivisions - 1, i + yDivisions, i))
    return polygons

def joinCornersWithQuad(xDivisions, yDivisions):
    return (0, yDivisions - 1, yDivisions * xDivisions - 1, yDivisions * (xDivisions - 1))
