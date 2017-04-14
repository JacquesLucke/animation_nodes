from ... data_structures cimport (
    DoubleList,
    Vector3DList,
    EdgeIndicesList
)

from ... math cimport (
    Vector3, distanceVec3
)

def createEdges(Vector3DList points1, Vector3DList points2):
    assert(len(points1) == len(points2))

    cdef Vector3DList newPoints = Vector3DList(length = len(points1) * 2)
    cdef EdgeIndicesList edges = EdgeIndicesList(length = len(points1))
    cdef Py_ssize_t i

    for i in range(len(points1)):
        newPoints.data[2 * i + 0] = points1.data[i]
        newPoints.data[2 * i + 1] = points2.data[i]
        edges.data[i].v1 = 2 * i + 0
        edges.data[i].v2 = 2 * i + 1

    return newPoints, edges

def calculateEdgeLengths(Vector3DList vertices, EdgeIndicesList edges):
    if len(edges) == 0:
        return DoubleList()

    if edges.getMaxIndex() >= len(vertices):
        raise Exception("Edges are invalid")

    cdef DoubleList distances = DoubleList(length = len(edges))
    cdef Py_ssize_t i
    cdef Vector3 *v1
    cdef Vector3 *v2
    for i in range(len(edges)):
        v1 = vertices.data + edges.data[i].v1
        v2 = vertices.data + edges.data[i].v2
        distances.data[i] = distanceVec3(v1, v2)
    return distances
