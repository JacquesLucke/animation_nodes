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
    cdef unsigned int v1, v2
    cdef IntegerList neighbours = IntegerList(length = edgesAmount * 2)
    for i in range(edgesAmount):
        v1, v2 = edges.data[i].v1, edges.data[i].v2
        neighbours.data[neighboursStarts.data[v1] + filledSpaces.data[v1]] = v2
        filledSpaces.data[v1] += 1

        neighbours.data[neighboursStarts.data[v2] + filledSpaces.data[v2]] = v1
        filledSpaces.data[v2] += 1

    # Generate Splines.
    cdef list splines = []
    cdef PolySpline spline
    cdef FloatList splineRadii
    cdef Vector3DList splineVertices
    cdef int currentVertex, nextVertex
    for i in range(verticesAmount):
        if neighboursAmounts.data[i] == 2: continue
        for j in range(neighboursAmounts.data[i]):
            currentVertex = i
            nextVertex = neighbours.data[neighboursStarts.data[i] + j]
            if (filledSpaces.data[nextVertex] == neighboursAmounts.data[nextVertex] or
                                                neighboursAmounts.data[nextVertex] != 2):
                splineVertices = Vector3DList.__new__(Vector3DList)
                splineRadii = FloatList.__new__(FloatList)

                splineVertices.append_LowLevel(vertices.data[currentVertex])
                splineRadii.append_LowLevel(radii.get(currentVertex))
                filledSpaces.data[currentVertex] -= 1
                while True:
                    if neighbours.data[neighboursStarts.data[nextVertex]] == currentVertex:
                        currentVertex = nextVertex
                        nextVertex = neighbours.data[neighboursStarts.data[nextVertex] + 1]
                    else:
                        currentVertex = nextVertex
                        nextVertex = neighbours.data[neighboursStarts.data[nextVertex]]
                    splineVertices.append_LowLevel(vertices.data[currentVertex])
                    splineRadii.append_LowLevel(radii.get(currentVertex))
                    filledSpaces.data[currentVertex] -= 1
                    if neighboursAmounts.data[currentVertex] != 2:
                        break
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
