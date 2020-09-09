from ... data_structures import GPStroke
from ... data_structures cimport (
    Mesh,
    LongList,
    ColorList,
    FloatList,
    PolySpline,
    DoubleList,
    BooleanList,
    Vector3DList,
)

from libc.math cimport INFINITY
from . line import getLinesMesh
from ... math cimport distanceVec3

# Dijkstra's algorithm (https://en.wikipedia.org/wiki/Dijkstra%27s_algorithm) but is implemented
# such a way to handle multi-sources and mesh with multiple islands.
def getShortestPath(Mesh mesh, LongList sources, LongList targets, str pathType, str mode):
    cdef Vector3DList vertices = mesh.vertices
    cdef long vertexCount = vertices.length
    cdef float maxDistance = INFINITY
    cdef DoubleList distances = DoubleList.fromValue(maxDistance, length = vertexCount)
    cdef LongList previousVertices = LongList.fromValue(-1, length = vertexCount)
    cdef BooleanList visitedVertices = BooleanList.fromValue(False, length = vertexCount)
    cdef Py_ssize_t i, targetIndex

    for i in range (sources.length):
        distances.data[sources.data[i]] = 0.0

    if mode == "PATH":
        targetIndex = targets.data[0]
    else:
        targetIndex = <int>INFINITY

    cdef float distance, minDistance
    cdef Py_ssize_t k, l, currentIndex, neighboursStart, neighbourIndex
    cdef LongList neighboursAmounts, neighboursStarts, neighbours
    neighboursAmounts, neighboursStarts, neighbours = mesh.getLinkedVertices()[:3]

    for i in range(vertexCount):

        minDistance = maxDistance
        for k in range(vertexCount):
            distance = distances.data[k]
            if distance < minDistance and not visitedVertices.data[k]:
                minDistance = distance

        if minDistance == maxDistance:
            break

        for currentIndex in range(vertexCount):
            if abs(minDistance - distances.data[currentIndex]) < 1.0e-6:
                visitedVertices.data[currentIndex] = True

                neighboursStart = neighboursStarts.data[currentIndex]
                for l in range(neighboursAmounts.data[currentIndex]):
                    neighbourIndex = neighbours.data[neighboursStart + l]
                    distance = (distanceVec3(vertices.data + currentIndex, vertices.data + neighbourIndex)
                                + distances.data[currentIndex])
                    if distance < distances.data[neighbourIndex]:
                        distances.data[neighbourIndex] = distance
                        previousVertices.data[neighbourIndex] = currentIndex
                        if currentIndex == targetIndex: break

    cdef LongList indices
    cdef Py_ssize_t index

    if mode == "PATH":
        indices = LongList()
        index = targetIndex
        if previousVertices.data[index] == -1: return indices
        for j in range(vertexCount):
            indices.append(index)
            index = previousVertices.data[index]
            if index == -1: break

        return indices.reversed()

    cdef Vector3DList sortLocations
    cdef list tree = []

    for i in range(vertexCount):
        sortLocations = Vector3DList()
        index = i
        if previousVertices.data[index] == -1: continue
        for j in range(vertexCount):
            sortLocations.append(vertices[index])
            index = previousVertices.data[index]
            if index == -1: break

        tree.append(outputPath(pathType, sortLocations))

    return tree

def outputPath(str pathType, Vector3DList sortLocations):
    cdef long amount
    if pathType == "MESH":
        return getLinesMesh(sortLocations.reversed(), False)
    elif pathType == "SPLINE":
        return PolySpline.__new__(PolySpline, sortLocations.reversed())
    elif pathType == "STROKE":
        amount = sortLocations.length
        strengths = FloatList(length = amount)
        pressures = FloatList(length = amount)
        uvRotations = FloatList(length = amount)
        vertexColors = ColorList(length = amount)
        strengths.fill(1)
        pressures.fill(1)
        uvRotations.fill(0)
        vertexColors.fill((0, 0, 0, 0))
        return GPStroke(sortLocations.reversed(), strengths, pressures, uvRotations, vertexColors, 10)
