from ... math cimport lengthVec3
from libc.string cimport memset
from cpython.mem cimport PyMem_Malloc, PyMem_Realloc, PyMem_Free
from ... data_structures cimport (
    Vector3DList,
    PolygonIndicesList,
    EdgeIndicesList,
    VirtualDoubleList,
    Mesh
)

def solidify(Mesh mesh, int loops = 0):
    cdef int i, j, vertexIndex, boundaryIndex
    cdef double normalLength

    cdef Vector3DList vertices = mesh.vertices
    cdef Vector3DList normals = mesh.getVertexNormals()
    cdef EdgeIndicesList edges = mesh.edges
    cdef PolygonIndicesList polygons = mesh.polygons
    cdef unsigned int *polyLengths = polygons.polyLengths.data
    cdef unsigned int *polyStarts = polygons.polyStarts.data
    cdef unsigned int *polyIndices = polygons.indices.data
    cdef int verticesAmount = len(vertices)
    cdef int edgesAmount = len(edges)
    cdef int indicesAmount = len(polygons.indices)
    cdef int polygonsAmount = len(polygons.polyStarts)

    # =============================== Vertices ===============================
    cdef int *boundaryValues = <int*>PyMem_Malloc(verticesAmount * sizeof(int))
    memset(boundaryValues, 0, verticesAmount * sizeof(int))

    for i in range(edgesAmount):
        (boundaryValues + edges.data[i].v1)[0] += 1
        (boundaryValues + edges.data[i].v2)[0] += 1

    for i in range(polygonsAmount):
        for j in range(polyLengths[i]):
            (boundaryValues + polyIndices[polyStarts[i] + j])[0] -= 1

    cdef int boundaryCount = 0
    cdef int *boundaryIndices = <int*>PyMem_Malloc(verticesAmount * sizeof(int))
    for i in range(verticesAmount):
        if (boundaryValues + i)[0]:
            (boundaryIndices + boundaryCount)[0] = i
            boundaryCount += 1

    boundaryIndices = <int*>PyMem_Realloc(boundaryIndices, boundaryCount * sizeof(int))

    cdef Vector3DList newVertices = Vector3DList(length = verticesAmount * 2 + boundaryCount * loops)

    for i in range(verticesAmount):
        newVertices.data[i].x = vertices.data[i].x
        newVertices.data[i].y = vertices.data[i].y
        newVertices.data[i].z = vertices.data[i].z

    j = verticesAmount + boundaryCount * loops
    for i in range(verticesAmount):
        normalLength = lengthVec3(normals.data + i)
        vertexIndex = j + i
        newVertices.data[vertexIndex].x = vertices.data[i].x + normals.data[i].x / normalLength
        newVertices.data[vertexIndex].y = vertices.data[i].y + normals.data[i].y / normalLength
        newVertices.data[vertexIndex].z = vertices.data[i].z + normals.data[i].z / normalLength

    cdef float heightFactor = 1./(loops + 1)
    for i in range(boundaryCount):
        boundaryIndex = (boundaryIndices + i)[0]
        normalLength = lengthVec3(normals.data + boundaryIndex)
        for j in range(loops):
            vertexIndex = verticesAmount + j * boundaryCount + i
            j += 1
            newVertices.data[vertexIndex].x = (vertices.data[boundaryIndex].x +
            (normals.data[boundaryIndex].x / normalLength) * heightFactor * j)
            newVertices.data[vertexIndex].y = (vertices.data[boundaryIndex].y +
            (normals.data[boundaryIndex].y / normalLength) * heightFactor * j)
            newVertices.data[vertexIndex].z = (vertices.data[boundaryIndex].z +
            (normals.data[boundaryIndex].z / normalLength) * heightFactor * j)

    PyMem_Free(boundaryValues)
    PyMem_Free(boundaryIndices)



    return(newVertices)
