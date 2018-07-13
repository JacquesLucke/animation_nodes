from ... data_structures cimport (
    Mesh, Vector3DList, EdgeIndicesList, PolySpline,
    VirtualDoubleList, FloatList, IntegerList
)

def splinesFromBranches(Vector3DList vertices, EdgeIndicesList edges, VirtualDoubleList radii):
    cdef int i, j
    cdef int edgesAmount = edges.length
    cdef int verticesAmount = vertices.length

    # Compute how many neighbour each vertex have.
    cdef IntegerList neighboursAmounts = IntegerList.fromValue(0, length = verticesAmount)
    for i in range(edgesAmount):
        neighboursAmounts.data[edges.data[i].v1] += 1
        neighboursAmounts.data[edges.data[i].v2] += 1

    # Compute the start index of each group of neighbours of each vertex.
    cdef IntegerList neighboursStarts = IntegerList(length = verticesAmount)
    cdef int start = 0
    for i in range(verticesAmount):
        neighboursStarts.data[i] = start
        start += neighboursAmounts.data[i]

    # Keep track of how many index is in each group of neighbours at each iteration.
    cdef IntegerList filledSpaces = IntegerList.fromValue(0, length = verticesAmount)

    # Compute the indices of neighbouring vertices of each vertex.
    cdef IntegerList neighbours = IntegerList(length = edgesAmount * 2)
    for i in range(edgesAmount):
        neighbours.data[neighboursStarts.data[edges.data[i].v1] +
        filledSpaces.data[edges.data[i].v1]] = edges.data[i].v2
        filledSpaces.data[edges.data[i].v1] += 1

        neighbours.data[neighboursStarts.data[edges.data[i].v2] +
        filledSpaces.data[edges.data[i].v2]] = edges.data[i].v1
        filledSpaces.data[edges.data[i].v2] += 1

    # Find the indices of the vertices that are not connected to two vertices.
    cdef IntegerList nonBipolarVertices = IntegerList(length = verticesAmount)
    cdef int nonBipolarVertsCount = 0
    for i in range(verticesAmount):
        if neighboursAmounts.data[i] != 2:
            nonBipolarVertices.data[nonBipolarVertsCount] = i
            nonBipolarVertsCount += 1
    nonBipolarVertices.length = nonBipolarVertsCount
    nonBipolarVertices.shrinkToLength()

    # Generate Splines.
    cdef int count
    cdef list splines = []
    cdef PolySpline spline
    cdef FloatList splineRadii
    cdef Vector3DList splineVertices
    cdef int nonBipolarVertex, currentVertex, nextVertex
    for i in range(nonBipolarVertsCount):
        nonBipolarVertex = nonBipolarVertices.data[i]
        for j in range(neighboursAmounts.data[nonBipolarVertex]):
            nextVertex = neighbours.data[neighboursStarts.data[nonBipolarVertex] + j]
            if (filledSpaces.data[nextVertex] == neighboursAmounts.data[nextVertex] or
                                                neighboursAmounts.data[nextVertex] != 2):
                splineVertices = Vector3DList.__new__(Vector3DList, length = verticesAmount)
                splineRadii = FloatList.__new__(FloatList, length = verticesAmount)

                splineVertices.data[0] = vertices.data[nonBipolarVertex]
                splineRadii.data[0] = radii.get(nonBipolarVertex)
                splineVertices.data[1] = vertices.data[nextVertex]
                splineRadii.data[1] = radii.get(nextVertex)
                filledSpaces.data[nonBipolarVertex] -= 1
                filledSpaces.data[nextVertex] -= 1

                count = 2
                currentVertex = nonBipolarVertex
                while neighboursAmounts.data[nextVertex] == 2:
                    if neighbours.data[neighboursStarts.data[nextVertex]] == currentVertex:
                        currentVertex = nextVertex
                        nextVertex = neighbours.data[neighboursStarts.data[nextVertex] + 1]
                    else:
                        currentVertex = nextVertex
                        nextVertex = neighbours.data[neighboursStarts.data[nextVertex]]
                    splineVertices.data[count] = vertices.data[nextVertex]
                    splineRadii.data[count] = radii.get(nextVertex)
                    filledSpaces.data[nextVertex] -= 1
                    count += 1
                splineVertices.length = count
                splineRadii.length = count
                splines.append(PolySpline.__new__(PolySpline, splineVertices, splineRadii))

    return splines

def splinesFromEdges(Vector3DList vertices, EdgeIndicesList edges, VirtualDoubleList radii,
                     str radiusType):
    cdef:
        long i
        list splines = []
        Vector3DList edgeVertices
        FloatList edgeRadii
        bint radiusPerVertex = radiusType == "VERTEX"

    for i in range(edges.length):
        edgeVertices = Vector3DList.__new__(Vector3DList, length = 2)
        edgeVertices.data[0] = vertices.data[edges.data[i].v1]
        edgeVertices.data[1] = vertices.data[edges.data[i].v2]

        edgeRadii = FloatList.__new__(FloatList, length = 2)
        if radiusPerVertex:
            edgeRadii.data[0] = radii.get(edges.data[i].v1)
            edgeRadii.data[1] = radii.get(edges.data[i].v2)
        else:
            edgeRadii.data[0] = radii.get(i)
            edgeRadii.data[1] = radii.get(i)

        splines.append(PolySpline.__new__(PolySpline, edgeVertices, edgeRadii))
    return splines
