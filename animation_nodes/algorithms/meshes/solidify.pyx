from ... math cimport lengthVec3
from libc.string cimport memset
from cpython.mem cimport PyMem_Malloc, PyMem_Realloc, PyMem_Free
from ... data_structures.meshes.validate import createValidEdgesList
from ... data_structures cimport (
    Vector3DList,
    PolygonIndicesList,
    EdgeIndicesList,
    VirtualDoubleList,
    Mesh
)

def solidify(Mesh mesh, int loops, double thickness, VirtualDoubleList offsets):
    cdef int i, j
    cdef Vector3DList vertices = mesh.vertices
    cdef EdgeIndicesList edges = mesh.edges
    cdef PolygonIndicesList polygons = mesh.polygons
    cdef unsigned int *polyLengths = polygons.polyLengths.data
    cdef unsigned int *polyStarts = polygons.polyStarts.data
    cdef unsigned int *polyIndices = polygons.indices.data
    cdef int verticesAmount = len(vertices)
    cdef int edgesAmount = len(edges)
    cdef int indicesAmount = len(polygons.indices)
    cdef int polygonAmount = len(polygons.polyStarts)

    loops = max(loops, 0)

    # Normals
    cdef Vector3DList normals = mesh.getVertexNormals()
    cdef float *heightFactors = <float*>PyMem_Malloc(verticesAmount * sizeof(float))
    for i in range(verticesAmount):
        (heightFactors + i)[0] = (thickness + offsets.get(i)) / (lengthVec3(normals.data + i) * (loops + 1))

    # =============================== Vertices ===============================
    cdef int *boundaryValues = <int*>PyMem_Malloc(verticesAmount * sizeof(int))
    memset(boundaryValues, 0, verticesAmount * sizeof(int))

    for i in range(edgesAmount):
        (boundaryValues + edges.data[i].v1)[0] += 1
        (boundaryValues + edges.data[i].v2)[0] += 1

    for i in range(polygonAmount):
        for j in range(polyLengths[i]):
            (boundaryValues + polyIndices[polyStarts[i] + j])[0] -= 1

    cdef int boundaryCount = 0
    cdef int *boundaryIndices = <int*>PyMem_Malloc(verticesAmount * sizeof(int))
    cdef int *boundaryMap = <int*>PyMem_Malloc(verticesAmount * sizeof(int))
    for i in range(verticesAmount):
        (boundaryMap + i)[0] = boundaryCount + verticesAmount
        if (boundaryValues + i)[0]:
            (boundaryIndices + boundaryCount)[0] = i
            boundaryCount += 1

    boundaryIndices = <int*>PyMem_Realloc(boundaryIndices, boundaryCount * sizeof(int))

    cdef Vector3DList newVertices = Vector3DList(length = verticesAmount * 2 + boundaryCount * loops)

    for i in range(verticesAmount):
        newVertices.data[i].x = vertices.data[i].x
        newVertices.data[i].y = vertices.data[i].y
        newVertices.data[i].z = vertices.data[i].z

    cdef int vertexIndex
    j = verticesAmount + boundaryCount * loops
    for i in range(verticesAmount):
        vertexIndex = j + i
        newVertices.data[vertexIndex].x = (vertices.data[i].x + normals.data[i].x *
        (heightFactors + i)[0] * (loops + 1))
        newVertices.data[vertexIndex].y = (vertices.data[i].y + normals.data[i].y *
        (heightFactors + i)[0] * (loops + 1))
        newVertices.data[vertexIndex].z = (vertices.data[i].z + normals.data[i].z *
        (heightFactors + i)[0] * (loops + 1))

    cdef int boundaryIndex
    for i in range(boundaryCount):
        boundaryIndex = (boundaryIndices + i)[0]
        for j in range(loops):
            vertexIndex = verticesAmount + j * boundaryCount + i
            j += 1
            newVertices.data[vertexIndex].x = (vertices.data[boundaryIndex].x +
            normals.data[boundaryIndex].x * (heightFactors + boundaryIndex)[0] * j)
            newVertices.data[vertexIndex].y = (vertices.data[boundaryIndex].y +
            normals.data[boundaryIndex].y * (heightFactors + boundaryIndex)[0] * j)
            newVertices.data[vertexIndex].z = (vertices.data[boundaryIndex].z +
            normals.data[boundaryIndex].z * (heightFactors + boundaryIndex)[0] * j)

    # ============================= Polygons =============================
    cdef int *boundaryEdges = <int*>PyMem_Malloc(edgesAmount * sizeof(int))
    cdef int edgeCount = 0
    for i in range(edgesAmount):
        if (boundaryValues + edges.data[i].v1)[0] and (boundaryValues + edges.data[i].v2)[0]:
            (boundaryEdges + edgeCount)[0] = i
            edgeCount += 1
    boundaryEdges = <int*>PyMem_Realloc(boundaryEdges, edgeCount * sizeof(int))

    cdef PolygonIndicesList newPolygons = PolygonIndicesList(
        indicesAmount = indicesAmount * 2 + edgeCount * (loops + 1) * 4,
        polygonAmount = polygonAmount * 2 + edgeCount * (loops + 1))

    boundaryIndex = boundaryCount * (loops + 1)
    for i in range(polygonAmount):
        newPolygons.polyStarts.data[i] = polygons.polyStarts.data[i]
        newPolygons.polyLengths.data[i] = polygons.polyLengths.data[i]

        newPolygons.polyStarts.data[boundaryIndex + polygonAmount + i] = polygons.polyStarts.data[i] + indicesAmount + boundaryIndex * 4
        newPolygons.polyLengths.data[boundaryIndex + polygonAmount + i] = polygons.polyLengths.data[i]

        for j in range(polygons.polyLengths.data[i]):
            newPolygons.indices.data[polygons.polyStarts.data[i] + j] = (
            polygons.indices.data[polygons.polyStarts.data[i] + j])

            newPolygons.indices.data[(indicesAmount + boundaryIndex * 4 +
            polygons.polyStarts.data[i] + j)] = (
            polygons.indices.data[polygons.polyStarts.data[i] + j] +
            verticesAmount + boundaryCount * loops)

    # ========== Dummy ===========
    for i in range(boundaryIndex):
        newPolygons.polyStarts.data[polygonAmount + i] = indicesAmount + i * 4
        newPolygons.polyLengths.data[polygonAmount + i] = 4

        newPolygons.indices.data[indicesAmount + i * 4 + 0] = i
        newPolygons.indices.data[indicesAmount + i * 4 + 1] = i + 1
        newPolygons.indices.data[indicesAmount + i * 4 + 2] = i + 2
        newPolygons.indices.data[indicesAmount + i * 4 + 3] = i + 3

    cdef int v1, v2, vb1, vb2, polygonIndex, startIndex
    if loops:
        for i in range(edgeCount):
            v1 = edges.data[(boundaryEdges + i)[0]].v1
            v2 = edges.data[(boundaryEdges + i)[0]].v2

            polygonIndex = polygonAmount + i
            startIndex = indicesAmount + i * 4
            newPolygons.polyStarts.data[polygonIndex] = startIndex
            newPolygons.polyLengths.data[polygonIndex] = 4

            newPolygons.indices.data[startIndex + 0] = v1
            newPolygons.indices.data[startIndex + 1] = v2
            vb1 = (boundaryMap + v1)[0]
            vb2 = (boundaryMap + v2)[0]
            newPolygons.indices.data[startIndex + 2] = vb2
            newPolygons.indices.data[startIndex + 3] = vb1

            for j in range(loops - 1):
                polygonIndex = polygonAmount + (j + 1) * edgeCount + i
                startIndex = indicesAmount + ((j + 1) * edgeCount + i) * 4
                newPolygons.polyStarts.data[polygonIndex] = startIndex
                newPolygons.polyLengths.data[polygonIndex] = 4

                newPolygons.indices.data[startIndex + 0] = vb1 + j * boundaryCount
                newPolygons.indices.data[startIndex + 1] = vb2 + j * boundaryCount
                newPolygons.indices.data[startIndex + 2] = vb2 + (j + 1) * boundaryCount
                newPolygons.indices.data[startIndex + 3] = vb1 + (j + 1) * boundaryCount

            polygonIndex = polygonAmount + loops * edgeCount + i
            startIndex = indicesAmount + (loops * edgeCount + i) * 4
            newPolygons.polyStarts.data[polygonIndex] = startIndex
            newPolygons.polyLengths.data[polygonIndex] = 4

            newPolygons.indices.data[startIndex + 0] = vb1 + (loops - 1) * boundaryCount
            newPolygons.indices.data[startIndex + 1] = vb2 + (loops - 1) * boundaryCount
            newPolygons.indices.data[startIndex + 2] = v2 + loops * boundaryCount + verticesAmount
            newPolygons.indices.data[startIndex + 3] = v1 + loops * boundaryCount + verticesAmount
    else:
        for i in range(edgeCount):
            v1 = edges.data[(boundaryEdges + i)[0]].v1
            v2 = edges.data[(boundaryEdges + i)[0]].v2
            polygonIndex = polygonAmount + i
            startIndex = indicesAmount + i * 4
            newPolygons.polyStarts.data[polygonIndex] = startIndex
            newPolygons.polyLengths.data[polygonIndex] = 4

            newPolygons.indices.data[startIndex + 0] = v1
            newPolygons.indices.data[startIndex + 1] = v2
            newPolygons.indices.data[startIndex + 2] = v2 + verticesAmount
            newPolygons.indices.data[startIndex + 3] = v1 + verticesAmount

    PyMem_Free(boundaryIndices)
    PyMem_Free(boundaryValues)
    PyMem_Free(boundaryEdges)
    PyMem_Free(boundaryMap)
    return(Mesh(newVertices, createValidEdgesList(polygons = newPolygons), newPolygons,
                skipValidation = True))
