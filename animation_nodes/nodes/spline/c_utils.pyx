import cython
from ... data_structures.meshes.mesh_data import calculateCrossProducts
from .. mesh.c_utils import matricesFromNormalizedAxisData
from ... data_structures cimport (
    Vector3DList, EdgeIndicesList, FloatList,
    Spline, Matrix4x4List, VirtualFloatList
)
from ... algorithms.random_number_generators cimport XoShiRo256Plus
from ... math cimport scaleMatrix3x3Part, Vector3, subVec3, crossVec3, lengthSquaredVec3

def getMatricesAlongSpline(Spline spline, Py_ssize_t amount, distribution):
    assert spline.isEvaluable()
    spline.ensureNormals()
    cdef Vector3DList points = spline.getDistributedPoints(amount, distributionType = distribution)
    cdef Vector3DList tangents = spline.getDistributedTangents(amount, distributionType = distribution)
    cdef Vector3DList normals = spline.getDistributedNormals(amount, distributionType = distribution)
    cdef FloatList radii = spline.getDistributedRadii(amount, distributionType = distribution)

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

def getSplineAdaptiveParameters(Spline spline, float start, float end, float tolerance):
    cdef Vector3 startPoint, endPoint
    spline.evaluatePoint_LowLevel(start, &startPoint)
    spline.evaluatePoint_LowLevel(end, &endPoint)
    cdef FloatList parameters = FloatList()
    cdef XoShiRo256Plus rng = XoShiRo256Plus(0)
    adaptiveSample(spline, start, end, &startPoint, &endPoint, tolerance, rng, parameters)
    parameters.append_LowLevel(end)
    return parameters

@cython.cdivision(True)
cdef void adaptiveSample(Spline spline, float startParameter, float endParameter,
        Vector3 *startPoint, Vector3 *endPoint, float tolerance, XoShiRo256Plus rng,
        FloatList output):
    cdef center = (startParameter + endParameter) / 2
    cdef length = endParameter - startParameter
    cdef midParameter = rng.nextFloatInRange(center - length * 0.05, center + length * 0.05)
    cdef Vector3 midPoint
    spline.evaluatePoint_LowLevel(midParameter, &midPoint)

    if isSufficientlyFlat(startPoint, &midPoint, endPoint, tolerance):
        output.append_LowLevel(startParameter)
        return

    adaptiveSample(spline, startParameter, midParameter, startPoint, &midPoint,
        tolerance, rng, output)
    adaptiveSample(spline, midParameter, endParameter, &midPoint, endPoint,
        tolerance, rng, output)

cdef bint isSufficientlyFlat(Vector3 *start, Vector3 *middle, Vector3 *end, float tolerance):
    cdef Vector3 a, b, cross
    subVec3(&a, start, middle)
    subVec3(&b, end, middle)
    crossVec3(&cross, &a, &b)
    return lengthSquaredVec3(&cross) < tolerance * tolerance
