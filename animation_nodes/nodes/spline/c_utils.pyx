from ... data_structures.meshes.mesh_data import calculateCrossProducts
from .. mesh.c_utils import matricesFromNormalizedAxisData
from ... data_structures cimport (
    DoubleList, Vector3DList, EdgeIndicesList, FloatList,
    PolySpline, Spline, Matrix4x4List, VirtualFloatList
)
from ... math cimport scaleMatrix3x3Part

def splinesFromEdges(Vector3DList vertices, EdgeIndicesList edges, DoubleList radii, str radiusType):
    if edges.length == 0: return []
    if edges.getMaxIndex() >= vertices.length:
        raise Exception("Invalid edge indices")
    if radiusType == "EDGE":
        if edges.length != radii.length:
            raise Exception("wrong radius amount")
    elif radiusType == "VERTEX":
        if vertices.length != radii.length:
            raise Exception("wrong radius amount")

    cdef:
        long i
        list splines = []
        FloatList edgeRadii
        Vector3DList edgeVertices
        bint radiusPerVertex = radiusType == "VERTEX"

    for i in range(edges.length):
        edgeVertices = Vector3DList.__new__(Vector3DList, length = 2)
        edgeVertices.data[0] = vertices.data[edges.data[i].v1]
        edgeVertices.data[1] = vertices.data[edges.data[i].v2]

        edgeRadii = FloatList.__new__(FloatList, length = 2)
        if radiusPerVertex:
            edgeRadii.data[0] = radii.data[edges.data[i].v1]
            edgeRadii.data[1] = radii.data[edges.data[i].v2]
        else:
            edgeRadii.data[0] = radii.data[i]
            edgeRadii.data[1] = radii.data[i]

        splines.append(PolySpline.__new__(PolySpline, edgeVertices, edgeRadii))
    return splines

def getMatricesAlongSpline(Spline spline, Py_ssize_t amount):
    assert spline.isEvaluable()
    spline.ensureNormals()
    cdef Vector3DList points = spline.getDistributedPoints(amount)
    cdef Vector3DList tangents = spline.getDistributedTangents(amount)
    cdef Vector3DList normals = spline.getDistributedNormals(amount)
    cdef FloatList radii = spline.getDistributedRadii(amount)

    tangents.normalize()
    normals.normalize()
    cdef Vector3DList bitangents = calculateCrossProducts(normals, tangents)

    cdef Matrix4x4List matrices = matricesFromNormalizedAxisData(points, normals, bitangents, tangents)
    cdef Py_ssize_t i
    for i in range(amount):
        scaleMatrix3x3Part(matrices.data + i, radii.data[i])

    return matrices

def tiltSplinePoints(Spline spline, VirtualFloatList tilts, bint accumulate):
    cdef FloatList splineTilts = spline.tilts
    cdef Py_ssize_t i
    cdef float offset = 0
    if accumulate:
        for i in range(len(splineTilts)):
            offset += tilts.get(i)
            splineTilts.data[i] += offset
    else:
        for i in range(len(splineTilts)):
            splineTilts.data[i] += tilts.get(i)

    spline.markChanged()