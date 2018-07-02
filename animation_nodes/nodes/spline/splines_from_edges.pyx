from libc.string cimport memset
from ... data_structures cimport Mesh, Vector3DList, EdgeIndicesList, PolySpline
from cpython.mem cimport PyMem_Malloc, PyMem_Free

cdef connectedSplinesFromEdges(Mesh mesh):
    cdef int i
    cdef Vector3DList vertices = mesh.vertices
    cdef EdgeIndicesList edges = mesh.edges
    cdef int verticesAmount = len(vertices)
    cdef int edgesAmount = len(edges)

    # Compute how many neighbour does each vertex have.
    cdef int *neighboursAmounts = <int*>PyMem_Malloc(verticesAmount * sizeof(int))
    memset(neighboursAmounts, 0, verticesAmount * sizeof(int))
    for i in range(edgesAmount):
        (neighboursAmounts + edges.data[i].v1)[0] += 1
        (neighboursAmounts + edges.data[i].v2)[0] += 1

    # Compute the start index of each group of neighbours of each vertex.
    cdef int *neighboursStarts = <int*>PyMem_Malloc(verticesAmount * sizeof(int))
    cdef int start = 0
    for i in range(verticesAmount):
        (neighboursStarts + i)[0] = start
        start += (neighboursAmounts + i)[0]

    # Keep track of how many index was set in each group of neighbours.
    cdef int *filledSpaces = <int*>PyMem_Malloc(verticesAmount * sizeof(int))
    memset(filledSpaces, 0, verticesAmount * sizeof(int))

    # Compute the indices of neighbouring vertices of each vertex.
    cdef int *neighbours = <int*>PyMem_Malloc(edgesAmount * 2 * sizeof(int))
    for i in range(edgesAmount):
        (neighbours + (neighboursStarts + edges.data[i].v1)[0] + (filledSpaces + edges.data[i].v1)[0])[0] = edges.data[i].v2
        (filledSpaces + edges.data[i].v1)[0] += 1

        (neighbours + (neighboursStarts + edges.data[i].v2)[0] + (filledSpaces + edges.data[i].v2)[0])[0] = edges.data[i].v1
        (filledSpaces + edges.data[i].v2)[0] += 1
    PyMem_Free(filledSpaces)



    PyMem_Free(neighboursAmounts)
    PyMem_Free(neighboursStarts)
    PyMem_Free(neighbours)
