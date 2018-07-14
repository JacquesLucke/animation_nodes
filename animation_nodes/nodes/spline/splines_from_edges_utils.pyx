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
    cdef IntegerList usedSlots = IntegerList.fromValue(0, length = verticesAmount)

    # Compute the indices of neighbouring vertices of each vertex.
    cdef unsigned int v1, v2
    cdef IntegerList neighbours = IntegerList(length = edgesAmount * 2)
    for i in range(edgesAmount):
        v1, v2 = edges.data[i].v1, edges.data[i].v2
        neighbours.data[neighboursStarts.data[v1] + usedSlots.data[v1]] = v2
        usedSlots.data[v1] += 1

        neighbours.data[neighboursStarts.data[v2] + usedSlots.data[v2]] = v1
        usedSlots.data[v2] += 1

    # Generate Splines.
    cdef list splines = []
    cdef PolySpline spline
    cdef FloatList splineRadii
    cdef Vector3DList splineVertices
    cdef IntegerList unusedEdges = usedSlots
    del usedSlots

    cdef int startVertex, lastVertex, currentVertex, nextVertex
    cdef int offset, n1, n2

    for startVertex in range(verticesAmount):
        # is part of another spline
        if neighboursAmounts.data[startVertex] == 2:
            continue

        # has no unused outgoing edges
        if unusedEdges.data[startVertex] == 0:
            continue

        for j in range(neighboursAmounts.data[startVertex]):
            currentVertex = startVertex
            nextVertex = neighbours.data[neighboursStarts.data[currentVertex] + j]

            # check if this neighbour can be connected
            if unusedEdges.data[nextVertex] == 0:
                continue

            splineVertices = Vector3DList.__new__(Vector3DList)
            splineRadii = FloatList.__new__(FloatList)

            splineVertices.append_LowLevel(vertices.data[currentVertex])
            splineRadii.append_LowLevel(radii.get(currentVertex))

            # follow branch until the next non bipolar vertex
            while True:
                lastVertex = currentVertex
                currentVertex = nextVertex

                splineVertices.append_LowLevel(vertices.data[currentVertex])
                splineRadii.append_LowLevel(radii.get(currentVertex))
                unusedEdges.data[lastVertex] -= 1
                unusedEdges.data[currentVertex] -= 1

                # stop at another non bipolar vertex
                if neighboursAmounts.data[currentVertex] != 2:
                    break

                # choose next vertex to be the one we are not coming from
                offset = neighboursStarts.data[currentVertex]
                n1 = neighbours.data[offset + 0]
                n2 = neighbours.data[offset + 1]
                nextVertex = n1 if lastVertex != n1 else n2

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
