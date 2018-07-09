from libc.string cimport memset
from cpython.mem cimport PyMem_Malloc, PyMem_Realloc, PyMem_Free
from ... data_structures cimport Mesh, Vector3DList, EdgeIndicesList, PolySpline

def connectedSplinesFromEdges(Mesh mesh):
    cdef int i, j
    cdef Vector3DList vertices = mesh.vertices
    cdef EdgeIndicesList edges = mesh.edges
    cdef int verticesAmount = len(vertices)
    cdef int edgesAmount = len(edges)

    # Compute how many neighbour each vertex have.
    cdef int *neighboursAmounts = <int*>PyMem_Malloc(verticesAmount * sizeof(int))
    memset(neighboursAmounts, 0, verticesAmount * sizeof(int))
    for i in range(edgesAmount):
        neighboursAmounts[edges.data[i].v1] += 1
        neighboursAmounts[edges.data[i].v2] += 1

    # Compute the start index of each group of neighbours of each vertex.
    cdef int *neighboursStarts = <int*>PyMem_Malloc(verticesAmount * sizeof(int))
    cdef int start = 0
    for i in range(verticesAmount):
        neighboursStarts[i] = start
        start += neighboursAmounts[i]

    # Keep track of how many index is in each group of neighbours at each iteration.
    cdef int *filledSpaces = <int*>PyMem_Malloc(verticesAmount * sizeof(int))
    memset(filledSpaces, 0, verticesAmount * sizeof(int))

    # Compute the indices of neighbouring vertices of each vertex.
    cdef int *neighbours = <int*>PyMem_Malloc(edgesAmount * 2 * sizeof(int))
    for i in range(edgesAmount):
        neighbours[neighboursStarts[edges.data[i].v1] + filledSpaces[edges.data[i].v1]] = edges.data[i].v2
        filledSpaces[edges.data[i].v1] += 1

        neighbours[neighboursStarts[edges.data[i].v2] + filledSpaces[edges.data[i].v2]] = edges.data[i].v1
        filledSpaces[edges.data[i].v2] += 1

    # Find the indices of the vertices that are not connected to two vertices.
    cdef int *nonBipolarVertices = <int*>PyMem_Malloc(verticesAmount * sizeof(int))
    cdef int nonBipolarVertsCount = 0
    for i in range(verticesAmount):
        if neighboursAmounts[i] != 2:
            nonBipolarVertices[nonBipolarVertsCount] = i
            nonBipolarVertsCount += 1
    nonBipolarVertices = <int*>PyMem_Realloc(nonBipolarVertices, nonBipolarVertsCount * sizeof(int))

    # Generate Splines.
    cdef list splines = []
    cdef PolySpline spline
    cdef Vector3DList splineVertices
    cdef int nonBipolarVertex, currentVertex, nextVertex
    for i in range(nonBipolarVertsCount):
        nonBipolarVertex = nonBipolarVertices[i]
        for j in range(neighboursAmounts[nonBipolarVertex]):
            nextVertex = neighbours[neighboursStarts[nonBipolarVertex] + j]
            if filledSpaces[nextVertex] == neighboursAmounts[nextVertex]:
                splineVertices = Vector3DList(capacity = verticesAmount)
                splineVertices.append(vertices[nonBipolarVertex])
                splineVertices.append(vertices[nextVertex])
                filledSpaces[nonBipolarVertex] -= 1
                filledSpaces[nextVertex] -= 1
                currentVertex = nonBipolarVertex
                for _ in range(verticesAmount):
                    if neighboursAmounts[nextVertex] == 2:
                        i = currentVertex
                        currentVertex = nextVertex
                        if neighbours[neighboursStarts[nextVertex]] == i:
                            nextVertex = neighbours[neighboursStarts[nextVertex] + 1]
                        else:
                            nextVertex = neighbours[neighboursStarts[nextVertex]]
                        splineVertices.append(vertices[nextVertex])
                        filledSpaces[nextVertex] -= 1
                    else:
                        break
                splines.append(PolySpline(splineVertices))

    PyMem_Free(nonBipolarVertices)
    PyMem_Free(neighboursAmounts)
    PyMem_Free(neighboursStarts)
    PyMem_Free(filledSpaces)
    PyMem_Free(neighbours)

    return splines
