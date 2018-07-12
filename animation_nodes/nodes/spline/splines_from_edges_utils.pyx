from libc.string cimport memset
from cpython.mem cimport PyMem_Malloc, PyMem_Realloc, PyMem_Free
from ... data_structures cimport (
    Mesh, Vector3DList, EdgeIndicesList, PolySpline,
    VirtualDoubleList, FloatList
)

def splinesFromBranches(Vector3DList vertices, EdgeIndicesList edges, VirtualDoubleList radii):
    cdef int i, j
    cdef int edgesAmount = edges.length
    cdef int verticesAmount = vertices.length

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
    cdef int count
    cdef list splines = []
    cdef PolySpline spline
    cdef FloatList splineRadii
    cdef Vector3DList splineVertices
    cdef int nonBipolarVertex, currentVertex, nextVertex
    for i in range(nonBipolarVertsCount):
        nonBipolarVertex = nonBipolarVertices[i]
        for j in range(neighboursAmounts[nonBipolarVertex]):
            nextVertex = neighbours[neighboursStarts[nonBipolarVertex] + j]
            if (filledSpaces[nextVertex] == neighboursAmounts[nextVertex] or
                                           neighboursAmounts[nextVertex] != 2):
                splineVertices = Vector3DList.__new__(Vector3DList, length = verticesAmount)
                splineRadii = FloatList.__new__(FloatList, length = verticesAmount)

                splineVertices.data[0] = vertices.data[nonBipolarVertex]
                splineRadii.data[0] = radii.get(nonBipolarVertex)
                splineVertices.data[1] = vertices.data[nextVertex]
                splineRadii.data[1] = radii.get(nextVertex)
                filledSpaces[nonBipolarVertex] -= 1
                filledSpaces[nextVertex] -= 1

                count = 2
                currentVertex = nonBipolarVertex
                while neighboursAmounts[nextVertex] == 2:
                    if neighbours[neighboursStarts[nextVertex]] == currentVertex:
                        currentVertex = nextVertex
                        nextVertex = neighbours[neighboursStarts[nextVertex] + 1]
                    else:
                        currentVertex = nextVertex
                        nextVertex = neighbours[neighboursStarts[nextVertex]]
                    splineVertices.data[count] = vertices.data[nextVertex]
                    splineRadii.data[count] = radii.get(nextVertex)
                    filledSpaces[nextVertex] -= 1
                    count += 1
                splineVertices.length = count
                splineRadii.length = count
                splines.append(PolySpline.__new__(PolySpline, splineVertices, splineRadii))

    PyMem_Free(nonBipolarVertices)
    PyMem_Free(neighboursAmounts)
    PyMem_Free(neighboursStarts)
    PyMem_Free(filledSpaces)
    PyMem_Free(neighbours)

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
