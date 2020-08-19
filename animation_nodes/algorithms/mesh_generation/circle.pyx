from libc.math cimport sin, cos
from libc.math cimport M_PI as PI
from ... data_structures.meshes.validate import createValidEdgesList
from ... data_structures cimport (
    Vector3DList, EdgeIndicesList, PolygonIndicesList,
    Mesh, VirtualDoubleList, VirtualLongList, LongList,
)


def getCircleMesh(Py_ssize_t radialLoops, Py_ssize_t innerLoops,
                  double outerRadius, double innerRadius,
                  double startAngle, double endAngle,
                  bint mergeStartEnd, bint mergeCenter):

    cdef PolygonIndicesList polygonsIndices = polygons(radialLoops, innerLoops,
                                                       mergeStartEnd, mergeCenter)
    cdef LongList materialIndices = LongList(length = polygonsIndices.getLength())
    materialIndices.fill(0)

    return Mesh(vertices(radialLoops, innerLoops, outerRadius, innerRadius,
                         startAngle, endAngle, mergeStartEnd, mergeCenter),
                         createValidEdgesList(polygons = polygonsIndices), polygonsIndices,
                         materialIndices, skipValidation = True)

def getCircleMeshList(Py_ssize_t amount,
                      VirtualLongList radialLoops,
                      VirtualLongList innerLoops,
                      VirtualDoubleList outerRadius,
                      VirtualDoubleList innerRadius,
                      VirtualDoubleList startAngle,
                      VirtualDoubleList endAngle,
                      bint mergeStartEnd,
                      bint mergeCenter):

    cdef list meshes = []
    cdef Py_ssize_t i
    cdef PolygonIndicesList polygonsIndices
    cdef LongList materialIndices
    for i in range(amount):
        polygonsIndices = polygons(radialLoops.get(i), innerLoops.get(i),
                                   mergeStartEnd, mergeCenter)
        materialIndices = LongList(length = polygonsIndices.getLength())
        materialIndices.fill(0)

        meshes.append(Mesh(vertices(radialLoops.get(i),  innerLoops.get(i),
                                    outerRadius.get(i), innerRadius.get(i),
                                    startAngle.get(i), endAngle.get(i),
                                    mergeStartEnd, mergeCenter),
                                    createValidEdgesList(polygons = polygonsIndices),
                                    polygonsIndices, materialIndices,
                                    skipValidation = True))

    return meshes


cdef vertices(Py_ssize_t radialLoops, Py_ssize_t innerLoops,
              double outerRadius, double innerRadius,
              double startAngle, double endAngle,
              bint mergeStartEnd, bint mergeCenter):

    radialLoops = max(radialLoops, 3)
    innerLoops = max(innerLoops, 0)

    cdef:
        Py_ssize_t i, j, numVerts, dummyIndex
        Vector3DList vertices
        double innerStep, angleStep, iCos, iSin, stepCos, stepSin, iRadius, newCos

    numVerts = radialLoops * (innerLoops + 1 + (not mergeCenter)) + mergeCenter
    vertices = Vector3DList(length = numVerts, capacity = numVerts)

    innerStep = (outerRadius if mergeCenter else outerRadius - innerRadius) / (innerLoops + 1)
    angleStep = (2 * PI if mergeStartEnd else endAngle - startAngle) / (radialLoops if mergeStartEnd else radialLoops - 1)
    iCos = cos(startAngle)
    iSin = sin(startAngle)
    stepCos = cos(angleStep)
    stepSin = sin(angleStep)

    for i in range(radialLoops):
        for j in range(innerLoops + 1 + (not mergeCenter)):
            iRadius = outerRadius - innerStep * j
            dummyIndex = j * radialLoops + i
            vertices.data[dummyIndex].x = iCos * iRadius
            vertices.data[dummyIndex].y = iSin * iRadius
            vertices.data[dummyIndex].z = 0

        newCos = stepCos * iCos - stepSin * iSin
        iSin = stepSin * iCos + stepCos * iSin
        iCos = newCos

    if mergeCenter:
        dummyIndex = numVerts - 1
        vertices.data[dummyIndex].x = 0
        vertices.data[dummyIndex].y = 0
        vertices.data[dummyIndex].z = 0

    return vertices


cdef polygons(Py_ssize_t radialLoops, Py_ssize_t innerLoops,
              bint mergeStartEnd, bint mergeCenter):

    radialLoops = max(radialLoops, 3)
    innerLoops = max(innerLoops, 0)

    cdef:
        PolygonIndicesList polygons
        Py_ssize_t i, polygonAmount, indicesAmount, dummyIndex, dummyIndexII

    polygonAmount = (radialLoops - 1 * (not mergeStartEnd)) * (innerLoops + 1)
    if mergeCenter:
        indicesAmount = (radialLoops - 1 * (not mergeStartEnd)) * (innerLoops * 4 + 3)
    else:
        indicesAmount = (innerLoops + 1) * (radialLoops - 1 * (not mergeStartEnd)) * 4

    polygons = PolygonIndicesList(
        indicesAmount = indicesAmount,
        polygonAmount = polygonAmount)

    if mergeStartEnd:
        for i in range((radialLoops - 1) * (innerLoops + 1 * (not mergeCenter))):
            dummyIndex = i + i//(radialLoops - 1)
            dummyIndexII = dummyIndex * 4
            polygons.polyStarts.data[dummyIndex] = dummyIndexII
            polygons.polyLengths.data[dummyIndex] = 4

            polygons.indices.data[dummyIndexII + 0] = dummyIndex
            polygons.indices.data[dummyIndexII + 1] = dummyIndex + 1
            polygons.indices.data[dummyIndexII + 2] = dummyIndex + radialLoops + 1
            polygons.indices.data[dummyIndexII + 3] = dummyIndex + radialLoops
        for i in range(innerLoops + 1 * (not mergeCenter)):
            dummyIndex = i * radialLoops + radialLoops - 1
            dummyIndexII = 4 * dummyIndex
            polygons.polyStarts.data[dummyIndex] = dummyIndexII
            polygons.polyLengths.data[dummyIndex] = 4

            polygons.indices.data[dummyIndexII + 0] = dummyIndex
            polygons.indices.data[dummyIndexII + 1] = dummyIndex - radialLoops + 1
            polygons.indices.data[dummyIndexII + 2] = dummyIndex + 1
            polygons.indices.data[dummyIndexII + 3] = dummyIndex + radialLoops
    else:
        for i in range((radialLoops - 1) * (innerLoops + 1 * (not mergeCenter))):
            dummyIndex = i + i//(radialLoops - 1)
            dummyIndexII = i * 4
            polygons.polyStarts.data[i] = dummyIndexII
            polygons.polyLengths.data[i] = 4

            polygons.indices.data[dummyIndexII + 0] = dummyIndex
            polygons.indices.data[dummyIndexII + 1] = dummyIndex + 1
            polygons.indices.data[dummyIndexII + 2] = dummyIndex + radialLoops + 1
            polygons.indices.data[dummyIndexII + 3] = dummyIndex + radialLoops

    if mergeCenter:
        polygonAmount = innerLoops * (radialLoops - 1 * (not mergeStartEnd))
        indicesAmount = polygonAmount * 4
        dummyIndex = radialLoops * innerLoops
        dummyIndexII = dummyIndex + radialLoops
        for i in range(radialLoops - 1):
            polygons.polyStarts.data[polygonAmount] = indicesAmount
            polygons.polyLengths.data[polygonAmount] = 3

            polygons.indices.data[indicesAmount + 0] = dummyIndex
            polygons.indices.data[indicesAmount + 1] = dummyIndex + 1
            polygons.indices.data[indicesAmount + 2] = dummyIndexII

            dummyIndex += 1
            polygonAmount += 1
            indicesAmount += 3

        if mergeStartEnd:
            polygons.polyStarts.data[polygonAmount] = indicesAmount
            polygons.polyLengths.data[polygonAmount] = 3

            polygons.indices.data[indicesAmount + 0] = dummyIndexII - 1
            polygons.indices.data[indicesAmount + 1] = dummyIndexII - radialLoops
            polygons.indices.data[indicesAmount + 2] = dummyIndexII

    return polygons

def getPointsOnCircle(Py_ssize_t amount, float radius = 1):
    assert amount > 0
    cdef Vector3DList points = Vector3DList(length = amount)

    cdef Py_ssize_t i
    cdef float factor = PI / <float>amount * 2
    for i in range(amount):
        points.data[i].x = cos(i * factor) * radius
        points.data[i].y = sin(i * factor) * radius
        points.data[i].z = 0

    return points
