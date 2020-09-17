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
def getShortestPath(Mesh mesh, LongList sources, Py_ssize_t target):
    cdef LongList previousVertices = computeShortestPathTree(mesh, sources, target)
    cdef LongList indices
    cdef Py_ssize_t index

    indices = LongList()
    index = target
    if previousVertices.data[index] == -1: return indices
    while index != -1:
        indices.append(index)
        index = previousVertices.data[index]

    return indices.reversed()

def getShortestTree(Mesh mesh, LongList sources, str pathType):
    cdef Vector3DList vertices = mesh.vertices
    cdef long vertexCount = vertices.length
    cdef LongList previousVertices = LongList(length = vertexCount)
    previousVertices = computeShortestPathTree(mesh, sources)

    cdef Vector3DList sortLocations
    cdef Py_ssize_t i, index
    cdef list tree = []

    for i in range(vertexCount):
        sortLocations = Vector3DList()
        index = i
        if previousVertices.data[index] == -1: continue
        while index != -1:
            sortLocations.append(vertices[index])
            index = previousVertices.data[index]

        tree.append(constructPath(pathType, sortLocations))

    return tree

def constructPath(str pathType, Vector3DList sortLocations):
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

cdef LongList computeShortestPathTree(Mesh mesh, LongList sources, Py_ssize_t target = -1):
    cdef Vector3DList vertices = mesh.vertices
    cdef long vertexCount = vertices.length
    cdef float maxDistance = INFINITY
    cdef DoubleList distances = DoubleList.fromValue(maxDistance, length = vertexCount)
    cdef LongList previousVertices = LongList.fromValue(-1, length = vertexCount)
    cdef BooleanList visitedVertices = BooleanList.fromValue(False, length = vertexCount)
    cdef Py_ssize_t i

    for i in range (sources.length):
        distances.data[sources.data[i]] = 0.0

    cdef float distance, minDistance
    cdef Py_ssize_t numberOfVisitedVertices = 0
    cdef Py_ssize_t j, minDistanceIndex, neighboursStart, neighbourIndex
    cdef LongList neighboursAmounts, neighboursStarts, neighbours
    neighboursAmounts, neighboursStarts, neighbours = mesh.getLinkedVertices()[:3]

    while numberOfVisitedVertices != vertexCount:
        minDistance = maxDistance

        for j in range(vertexCount):
            distance = distances.data[j]
            if distance < minDistance and not visitedVertices.data[j]:
                minDistance = distance
                minDistanceIndex = j

        numberOfVisitedVertices += 1
        visitedVertices.data[minDistanceIndex] = True

        neighboursStart = neighboursStarts.data[minDistanceIndex]
        for j in range(neighboursAmounts.data[minDistanceIndex]):
            neighbourIndex = neighbours.data[neighboursStart + j]
            distance = (distanceVec3(vertices.data + minDistanceIndex, vertices.data + neighbourIndex)
                        + distances.data[minDistanceIndex])
            if distance < distances.data[neighbourIndex]:
                distances.data[neighbourIndex] = distance
                previousVertices.data[neighbourIndex] = minDistanceIndex
                if minDistanceIndex == target: break

    return previousVertices
