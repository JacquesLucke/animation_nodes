from ... data_structures.lists.polygon_indices_list cimport PolygonIndicesList
from ... data_structures.lists.complex_lists cimport Vector3DList, EdgeIndicesList

# Vertices
############################################

def vertices(int xDivisions, int yDivisions, float xDistance = 1, float yDistance = 1, offset = (0, 0, 0)):
    assert xDivisions >= 2
    assert yDivisions >= 2
    cdef:
        float xOffset, yOffset, zOffset
        int x, y
    vertices = Vector3DList(length = xDivisions * yDivisions)
    xOffset, yOffset, zOffset = offset
    cdef int tmp
    for x in range(xDivisions):
        tmp = x * yDivisions
        for y in range(yDivisions):
            vertices.base.data[(tmp + y) * 3 + 0] = x * xDistance + xOffset
            vertices.base.data[(tmp + y) * 3 + 1] = y * yDistance + yOffset
            vertices.base.data[(tmp + y) * 3 + 2] = zOffset
    return vertices


# Edges
############################################

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


# Polygons
############################################


def quadPolygons(cls, xDivisions, yDivisions, joinHorizontal = False, joinVertical = False):
    polygons = PolygonIndicesList()
    polygons.extend(cls.innerQuadPolygons(xDivisions, yDivisions))
    if joinHorizontal:
        polygons.extend(cls.joinHorizontalEdgesQuadPolygons(xDivisions, yDivisions))
    if joinVertical:
        polygons.extend(cls.joinVerticalEdgesQuadPolygons(xDivisions, yDivisions))
    if joinHorizontal and joinVertical:
        polygons.append(cls.joinCornersWithQuad(xDivisions, yDivisions))
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
            polygons.indices.data[offset + 0] = (j + 0) * yDivisions + i
            polygons.indices.data[offset + 1] = (j + 0) * yDivisions + i + 1
            polygons.indices.data[offset + 2] = (j + 1) * yDivisions + i + 1
            polygons.indices.data[offset + 3] = (j + 1) * yDivisions + i
            offset += 4
    return polygons

def joinHorizontalEdgesQuadPolygons(xDivisions, yDivisions):
    polygons = []
    offset = yDivisions * (xDivisions - 1)
    for i in range(yDivisions - 1):
        polygons.append((i, i + offset, i + offset + 1, i + 1))
    return polygons

def joinVerticalEdgesQuadPolygons(xDivisions, yDivisions):
    polygons = []
    for i in range(0, (xDivisions - 1) * yDivisions, yDivisions):
        polygons.append((i, i + yDivisions, i + 2 * yDivisions - 1, i + yDivisions - 1))
    return polygons

def joinCornersWithQuad(xDivisions, yDivisions):
    return (0, yDivisions - 1, yDivisions * xDivisions - 1, yDivisions * (xDivisions - 1))
