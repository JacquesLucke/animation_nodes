# cython: profile=True
from ... data_structures cimport (
    Mesh,
    LongList,
    DoubleList,
    Vector3DList,
)

from . line import getLinesMesh
from ... math cimport distanceVec3

# Dijkstra's algorithm (https://en.wikipedia.org/wiki/Dijkstra%27s_algorithm) but is implemented such a way to handle multi-sources and mesh with multiple islands.
def getShortestPath(Mesh mesh, LongList sources):
    cdef Vector3DList vertices = mesh.vertices
    cdef long vertexCount = vertices.length
    cdef float maxWeight = 1000000
    cdef DoubleList weights = DoubleList.fromValue(maxWeight, length = vertexCount)
    cdef LongList visitedVertices = LongList.fromValue(0, length = vertexCount)
    cdef LongList previousVertices = LongList.fromValue(-1, length = vertexCount)
    cdef long i

    for i in range (sources.length):
        weights.data[sources.data[i]] = 0.0

    cdef LongList linkedVertices
    cdef long k, l, linkedIndex, currentIndex
    cdef float weight, minWeight

    for i in range(vertexCount):

        minWeight = maxWeight
        for k in range(vertexCount):
            weight = weights.data[k]
            if weight < minWeight and visitedVertices.data[k] == 0:
                minWeight = weight

        if minWeight == maxWeight:
            break

        for currentIndex in range(vertexCount):
            if abs(minWeight - weights.data[currentIndex]) < 1.0e-6:
                visitedVertices.data[currentIndex] = 1

                linkedVertices = mesh.getVertexLinkedVertices(currentIndex)[0]

                for l in range(linkedVertices.length):
                    linkedIndex = linkedVertices.data[l]
                    weight = distanceVec3(vertices.data + currentIndex, vertices.data + linkedIndex) + weights.data[currentIndex]
                    if weight < weights.data[linkedIndex]:
                        weights.data[linkedIndex] = weight
                        previousVertices.data[linkedIndex] = currentIndex

    cdef Vector3DList sortLocations
    cdef long index

    meshes = []
    for i in range(vertexCount):
        sortLocations = Vector3DList()
        index = i
        if previousVertices.data[index] == -1: continue
        for j in range(vertexCount):
            sortLocations.append(vertices[index])
            index = previousVertices.data[index]
            if index == -1: break
        meshes.append(getLinesMesh(sortLocations, False))

    return meshes
