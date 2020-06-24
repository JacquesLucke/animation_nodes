import cython
from libc.math cimport sqrt
from mathutils import Vector
from mathutils.kdtree import KDTree
from mathutils.bvhtree import BVHTree
from ... math cimport Vector3, distanceVec3
from ... algorithms.rotations.rotation_and_direction cimport directionToMatrix_LowLevel
from ... data_structures cimport (
    Mesh,
    LongList,
    FloatList,
    DoubleList,
    UIntegerList,
    Vector3DList,
    Matrix4x4List,
    PolygonIndicesList,
)
from ... math cimport (
    toVector3,
    scaleMatrix3x3Part,
    setTranslationMatrix,
    setMatrixTranslation,
    )

@cython.cdivision(True)
def dynamicRadiusSpherePacking(Vector3DList points, float margin, float radiusMax, float radiusStep,
                                 FloatList influences, bint mask, DoubleList objectRadii):
    cdef Py_ssize_t numberOfPoints = points.length
    kdTree = buildKDTree(numberOfPoints, points)

    cdef DoubleList radii = DoubleList(length = numberOfPoints)
    radii.fill(0)

    cdef float searchRadius = max(2 * (margin + radiusMax), 0)
    cdef DoubleList distances
    cdef LongList indices
    cdef float radius
    cdef Py_ssize_t i, iterations, numberOfNonZeroRadius

    numberOfNonZeroRadius = 0
    for i in range(numberOfPoints):
        indices, distances = calculateDistancesByRange(kdTree, points.data[i], searchRadius)
        iterations = int(radiusMax * influences.data[i] / radiusStep)
        radius = calulateMaxRadius(iterations, margin, radiusStep, radii, indices, distances)
        radii.data[i] = radius
        if radius > 0:
            numberOfNonZeroRadius += 1

    return calculateMatricesRadii(numberOfPoints, numberOfNonZeroRadius, points, radii, objectRadii, mask)

# Some reference https://www.youtube.com/watch?v=QHEQuoIKgNE
@cython.cdivision(True)
def neighbourRadiusSpherePacking(Vector3DList points, float margin, float radiusMax, float radiusStep,
                                 FloatList influences, bint mask, DoubleList objectRadii):
    cdef Py_ssize_t numberOfPoints = points.length
    kdTree = buildKDTree(numberOfPoints, points)

    cdef DoubleList radii = DoubleList(length = numberOfPoints)
    radii.fill(0)

    cdef LongList indices
    cdef DoubleList distances
    cdef float nextRadius, influence, radius
    cdef Py_ssize_t iterations = int(radiusMax / radiusStep)
    cdef Py_ssize_t i, numberOfNonZeroRadius

    numberOfNonZeroRadius = 0
    for j in range(iterations):
        numberOfNonZeroRadius = 0
        for i in range(numberOfPoints):
            nextRadius = radii.data[i] + radiusStep
            indices, distances = calculateDistancesByRange(kdTree, points.data[i], 2 * (margin + nextRadius))
            influence = influences.data[i]
            if comapareRadiusDistance(margin + nextRadius * influence, radii, indices, distances):
                radii.data[i] = nextRadius * influence
            if radii.data[i] > 0: numberOfNonZeroRadius += 1

    return calculateMatricesRadii(numberOfPoints, numberOfNonZeroRadius, points, radii, objectRadii, mask)

@cython.cdivision(True)
def fixedRadiusSpherePacking(Vector3DList points, float margin, DoubleList radii, FloatList influences, bint mask, DoubleList objectRadii):
    cdef Py_ssize_t numberOfPoints = points.length
    kdTree = buildKDTree(numberOfPoints, points)

    cdef float radius, searchRadius
    cdef DoubleList distances
    cdef LongList indices
    cdef Py_ssize_t i, numberOfNonZeroRadius

    numberOfNonZeroRadius = 0
    for i in range(numberOfPoints):
        radius = radii.data[i] * influences.data[i]
        searchRadius = max(2 * (radius + margin), 0)
        indices, distances = calculateDistancesByRange(kdTree, points.data[i], searchRadius)
        if comapareRadiusDistance(margin + radius, radii, indices, distances):
            radii.data[i] = radius
            numberOfNonZeroRadius += 1
        else:
            radii.data[i] = 0

    return calculateMatricesRadii(numberOfPoints, numberOfNonZeroRadius, points, radii, objectRadii, mask)


# Some reference http://www.codeplastic.com/2017/09/09/controlled-circle-packing-with-processing/
@cython.cdivision(True)
def relaxSpherePacking(Vector3DList points, float margin, DoubleList radii, float forceMagnitude,
                       Py_ssize_t iterations, float errorMax, Py_ssize_t neighbourAmount,
                       FloatList influences, bint mask, DoubleList objectRadii):
    cdef Py_ssize_t numberOfPoints = points.length
    cdef Vector3DList relaxPoints = points
    cdef Vector3DList prePoints = points
    cdef Vector3 point, force
    cdef DoubleList distances
    cdef LongList indices
    cdef float radius, totalRadius, distance, forceScale, error
    cdef Py_ssize_t i, j, k, count, index, numberOfNonZeroRadius

    numberOfNonZeroRadius = 0
    for i in range(numberOfPoints):
        radii.data[i] *= influences.data[i]
        if radii.data[i] > 0:
            numberOfNonZeroRadius += 1

    for k in range(iterations):
        count = 0
        kdTree = buildKDTree(numberOfPoints, relaxPoints)
        for j in range(numberOfPoints):
            radius = radii.data[j]
            point = relaxPoints.data[j]
            indices, distances = calculateDistancesByAmount(kdTree, point, 1 + neighbourAmount)

            if radius == 0: continue
            for i in range(1, indices.length):
                index = indices.data[i]
                distance = distances.data[i]

                totalRadius = margin + radius + radii.data[index]
                error = (totalRadius - distance) * 100 / totalRadius
                if distance > 0 and distance < totalRadius and error >= errorMax:
                    count += 1
                    forceScale = (totalRadius - distance) * forceMagnitude

                    force.x = point.x - relaxPoints.data[index].x
                    force.y = point.y - relaxPoints.data[index].y
                    force.z = point.z - relaxPoints.data[index].z

                    forceScale = forceScale / sqrt(force.x * force.x + force.y * force.y + force.z * force.z)

                    prePoints.data[j].x = point.x + force.x * forceScale
                    prePoints.data[j].y = point.y + force.y * forceScale
                    prePoints.data[j].z = point.z + force.z * forceScale

        relaxPoints.data = prePoints.data
        if count == 0: break

    return calculateMatricesRadii(numberOfPoints, numberOfNonZeroRadius, relaxPoints, radii, objectRadii, mask)

@cython.cdivision(True)
def relaxSpherePackingOnMesh(Vector3DList points, float margin, DoubleList radii, float forceMagnitude,
                             Py_ssize_t iterations, float errorMax, Py_ssize_t neighbourAmount, FloatList influences,
                             bint mask, DoubleList objectRadii, Vector3DList vertices, PolygonIndicesList polygons,
                             float maxDistance, float epsilon, bint alignToNormal):
    bvhTree = buildBVHTree(vertices, polygons, epsilon)
    cdef Py_ssize_t numberOfPoints = points.length
    cdef Vector3DList relaxPoints = points
    cdef Vector3DList prePoints = points
    cdef Vector3 point, force
    cdef DoubleList distances
    cdef LongList indices
    cdef float radius, totalRadius, distance, forceScale, error, x, y, z
    cdef Py_ssize_t i, j, k, count, index, numberOfNonZeroRadius

    numberOfNonZeroRadius = 0
    for i in range(numberOfPoints):
        radii.data[i] *= influences.data[i]
        if radii.data[i] > 0:
            numberOfNonZeroRadius += 1

    for k in range(iterations):
        count = 0
        kdTree = buildKDTree(numberOfPoints, relaxPoints)
        for j in range(numberOfPoints):
            radius = radii.data[j]
            point = relaxPoints.data[j]
            indices, distances = calculateDistancesByAmount(kdTree, point, 1 + neighbourAmount)

            if radius == 0: continue
            for i in range(1, indices.length):
                index = indices.data[i]
                distance = distances.data[i]

                totalRadius = margin + radius + radii.data[index]
                error = (totalRadius - distance) * 100 / totalRadius
                if distance > 0 and distance < totalRadius and error >= errorMax:
                    count += 1
                    forceScale = (totalRadius - distance) * forceMagnitude

                    force.x = point.x - relaxPoints.data[index].x
                    force.y = point.y - relaxPoints.data[index].y
                    force.z = point.z - relaxPoints.data[index].z
                    forceScale = forceScale / sqrt(force.x * force.x + force.y * force.y + force.z * force.z)

                    x = point.x + force.x * forceScale
                    y = point.y + force.y * forceScale
                    z = point.z + force.z * forceScale
                    bvhVector = bvhTree.find_nearest(Vector((x, y, z)), maxDistance)[0]
                    if bvhVector is not None:
                        prePoints.data[j] = toVector3(bvhVector)

        relaxPoints.data = prePoints.data
        if count == 0: break

    cdef Py_ssize_t totalMatrices = numberOfPoints
    if mask: totalMatrices = numberOfNonZeroRadius

    cdef Matrix4x4List matrices = Matrix4x4List(length = totalMatrices)
    cdef Vector3DList normals = Vector3DList(length = totalMatrices)
    cdef Vector3 guide = toVector3((0, 0, 1))
    cdef Vector3 normal = guide
    if not mask:
        if alignToNormal:
            for i in range(numberOfPoints):
                point = relaxPoints.data[i]
                bvhNormal = bvhTree.find_nearest(Vector((point.x, point.y, point.z)), maxDistance)[1]
                if bvhNormal is not None: normal = toVector3(bvhNormal)
                normals.data[i] = normal
                directionToMatrix_LowLevel(matrices.data + i, &normal, &guide, 2, 0)
                setMatrixTranslation(matrices.data + i, &point)
                radius = mapping(radii.data[i], 0, objectRadii.data[i], 0, 1)
                scaleMatrix3x3Part(matrices.data + i, radius)
            return matrices, radii, normals
        else:
            for i in range(numberOfPoints):
                bvhNormal = bvhTree.find_nearest(Vector((point.x, point.y, point.z)), maxDistance)[1]
                if bvhNormal is not None: normal = toVector3(bvhNormal)
                normals.data[i] = normal
                setTranslationMatrix(matrices.data + i, &relaxPoints.data[i])
                radius = mapping(radii.data[i], 0, objectRadii.data[i], 0, 1)
                scaleMatrix3x3Part(matrices.data + i, radius)
            return matrices, radii, normals

    cdef DoubleList newRadii = DoubleList(length = numberOfNonZeroRadius)
    index = 0

    if alignToNormal:
        for i in range(numberOfPoints):
            radius = radii.data[i]
            if radius > 0:
                radius = mapping(radius, 0, objectRadii.data[i], 0, 1)
                newRadii.data[index] = radius
                point = relaxPoints.data[i]
                bvhNormal = bvhTree.find_nearest(Vector((point.x, point.y, point.z)), maxDistance)[1]
                if bvhNormal is not None: normal = toVector3(bvhNormal)
                normals.data[i] = normal
                directionToMatrix_LowLevel(matrices.data + index, &normal, &guide, 2, 0)
                setMatrixTranslation(matrices.data + index, &point)
                scaleMatrix3x3Part(matrices.data + index, radius)
                index += 1
        return matrices, newRadii, normals
    else:
        for i in range(numberOfPoints):
            radius = radii.data[i]
            if radius > 0:
                radius = mapping(radius, 0, objectRadii.data[i], 0, 1)
                newRadii.data[index] = radius
                bvhNormal = bvhTree.find_nearest(Vector((point.x, point.y, point.z)), maxDistance)[1]
                if bvhNormal is not None: normal = toVector3(bvhNormal)
                normals.data[i] = normal
                setTranslationMatrix(matrices.data + index, &relaxPoints.data[i])
                scaleMatrix3x3Part(matrices.data + index, radius)
                index += 1
        return matrices, newRadii, normals


cdef calculateMatricesRadii(Py_ssize_t numberOfPoints, Py_ssize_t numberOfNonZeroRadius, Vector3DList points,
                            DoubleList radii, DoubleList objectRadii, bint mask):
    cdef Py_ssize_t totalMatrices = numberOfPoints
    if mask: totalMatrices = numberOfNonZeroRadius

    cdef Py_ssize_t i
    cdef Matrix4x4List matrices = Matrix4x4List(length = totalMatrices)
    if not mask:
        for i in range(numberOfPoints):
            radius = mapping(radii.data[i], 0, objectRadii.data[i], 0, 1)
            setTranslationMatrix(matrices.data + i, &points.data[i])
            scaleMatrix3x3Part(matrices.data + i, radius)
        return matrices, radii

    cdef DoubleList newRadii = DoubleList(length = numberOfNonZeroRadius)
    cdef Py_ssize_t index = 0
    for i in range(numberOfPoints):
        radius = radii.data[i]
        if radius > 0:
            radius = mapping(radius, 0, objectRadii.data[i], 0, 1)
            newRadii.data[index] = radius
            setTranslationMatrix(matrices.data + index, &points.data[i])
            scaleMatrix3x3Part(matrices.data + index, radius)
            index += 1
    return matrices, newRadii

@cython.cdivision(True)
cdef float mapping(float x, float xMin, float xMax, float yMin, float yMax):
    cdef float mapValue = yMin + (x - xMin) * (yMax - yMin) / (xMax - xMin)
    if mapValue > yMax: return yMax
    if mapValue < yMin: return yMin
    return mapValue

cdef float calulateMaxRadius(Py_ssize_t iterations, float margin, float radiusStep, DoubleList radii, LongList indices, DoubleList distances):
    cdef float newRadius = 0
    cdef Py_ssize_t i
    for i in range(iterations):
        if not comapareRadiusDistance(newRadius + margin, radii, indices, distances): break
        newRadius += radiusStep
    return newRadius

cdef bint comapareRadiusDistance(float newRadius, DoubleList radii, LongList indices, DoubleList distances):
    cdef bint newRadiusCheck = True
    cdef Py_ssize_t i
    for i in range(1, distances.length):
        if newRadius + radii.data[indices.data[i]] > distances.data[i]:
            newRadiusCheck = False
            break
    return newRadiusCheck

cdef calculateDistancesByRange(kdTree, Vector3 searchVector, float searchRadius):
    cdef list results = kdTree.find_range(Vector((searchVector.x, searchVector.y, searchVector.z)), searchRadius)
    cdef Py_ssize_t lenResult = len(results)
    cdef DoubleList distances = DoubleList(length = lenResult)
    cdef LongList indices = LongList(length = lenResult)
    cdef Py_ssize_t i
    for i in range(lenResult):
        result = results[i]
        indices.data[i] = result[1]
        distances.data[i] = result[2]
    return indices, distances

cdef calculateDistancesByAmount(kdTree, Vector3 searchVector, long amount):
    cdef list results = kdTree.find_n(Vector((searchVector.x, searchVector.y, searchVector.z)), amount)
    cdef Py_ssize_t lenResult = len(results)
    cdef DoubleList distances = DoubleList(length = lenResult)
    cdef LongList indices = LongList(length = lenResult)
    cdef Py_ssize_t i
    for i in range(lenResult):
        result = results[i]
        indices.data[i] = result[1]
        distances.data[i] = result[2]
    return indices, distances

cdef buildKDTree(Py_ssize_t numberOfPoints, Vector3DList points):
    kdTree = KDTree(numberOfPoints)
    cdef Vector3 vector
    cdef Py_ssize_t i
    for i in range(numberOfPoints):
        vector = points.data[i]
        kdTree.insert(Vector((vector.x, vector.y, vector.z)), i)
    kdTree.balance()
    return kdTree

cdef buildBVHTree(Vector3DList vertices, PolygonIndicesList polygons, epsilon):
    return BVHTree.FromPolygons(vertices, polygons, epsilon = max(epsilon, 0))


@cython.cdivision(True)
def spherePackingOnMesh(Vector3DList vertices, PolygonIndicesList polygons, bint alignToNormal, Vector3DList polyNormals,
                        FloatList influences, DoubleList objectRadii):
    cdef UIntegerList polyIndices = polygons.indices
    cdef UIntegerList polyStarts = polygons.polyStarts
    cdef Py_ssize_t polyAmount = polygons.getLength()
    cdef Matrix4x4List matrices = Matrix4x4List(length = polyAmount)
    cdef DoubleList inradii = DoubleList(length = polyAmount)
    cdef Vector3 vector1, vector2, vector3, incenter
    cdef Vector3 guide = toVector3((0, 0, 1))
    cdef double a, b, c, distance, s, area, inradius
    cdef Py_ssize_t i, start, polyIndex1, polyIndex2, polyIndex3

    for i in range (polyAmount):
        start = polyStarts.data[i]
        vector1 = vertices.data[polyIndices.data[start]]
        vector2 = vertices.data[polyIndices.data[start + 1]]
        vector3 = vertices.data[polyIndices.data[start + 2]]

        # Opposite edges
        a = distanceVec3(&vector2, &vector3)
        b = distanceVec3(&vector3, &vector1)
        c = distanceVec3(&vector1, &vector2)
        distance = a + b + c
        s = distance / 2.0

        inradius = sqrt(s * (s - a) * (s - b) * (s - c)) * min(influences.data[i], 1) / s
        inradii.data[i] = inradius

        incenter.x = (a * vector1.x + b * vector2.x + c * vector3.x) / distance
        incenter.y = (a * vector1.y + b * vector2.y + c * vector3.y) / distance
        incenter.z = (a * vector1.z + b * vector2.z + c * vector3.z) / distance

        if alignToNormal:
            directionToMatrix_LowLevel(matrices.data + i, polyNormals.data + i, &guide, 2, 0)
            setMatrixTranslation(matrices.data + i, &incenter)
        else:
            setTranslationMatrix(matrices.data + i, &incenter)
        inradius = mapping(inradius, 0, objectRadii.data[i], 0, 1)
        scaleMatrix3x3Part(matrices.data + i, inradius)

    return matrices, inradii
