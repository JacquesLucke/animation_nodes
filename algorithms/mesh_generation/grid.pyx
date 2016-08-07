from ... data_structures.lists.complex_lists cimport Vector3DList, EdgeIndicesList

# Vertices
############################################

def vertices(int xDivisions, int yDivisions, float xDistance = 1, float yDistance = 1, offset = (0, 0, 0)):
    assert xDivisions >= 0
    assert yDivisions >= 0
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

def innerQuadEdges(xDivisions, yDivisions):
    edges = EdgeIndicesList()
    for i in range((xDivisions - 1) * yDivisions):
        edges.append((i, i + yDivisions))
    for i in range(yDivisions - 1):
        for j in range(xDivisions):
            firstIndex = i + j * yDivisions
            edges.append((firstIndex, firstIndex + 1))
    return edges


# Polygons
############################################


def quadPolygons(cls, xDivisions, yDivisions, joinHorizontal = False, joinVertical = False):
    polygons = []
    polygons.extend(cls.innerQuadPolygons(xDivisions, yDivisions))
    if joinHorizontal:
        polygons.extend(cls.joinHorizontalEdgesQuadPolygons(xDivisions, yDivisions))
    if joinVertical:
        polygons.extend(cls.joinVerticalEdgesQuadPolygons(xDivisions, yDivisions))
    if joinHorizontal and joinVertical:
        polygons.append(cls.joinCornersWithQuad(xDivisions, yDivisions))
    return polygons

def innerQuadPolygons(xDivisions, yDivisions):
    polygons = []
    for i in range(0, (xDivisions - 1) * yDivisions, yDivisions):
        for j in range(i, i + yDivisions - 1):
            polygons.append((j, j + 1, j + yDivisions + 1, j + yDivisions))
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
