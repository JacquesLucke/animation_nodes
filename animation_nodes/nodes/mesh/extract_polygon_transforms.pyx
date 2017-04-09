import bpy
cimport cython
from bpy.props import *
from ... base_types import AnimationNode
from ... data_structures cimport Vector3DList, PolygonIndicesList, Matrix4x4List
from ... math cimport Vector3, Matrix4, scaleVec3, subVec3, crossVec3, normalizeVec3_InPlace

class ExtractPolygonTransformsNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_ExtractPolygonTransformsNode"
    bl_label = "Extract Polygon Transforms"

    errorMessage = StringProperty()

    def create(self):
        self.newInput("Vector List", "Vertices", "vertices")
        self.newInput("Polygon Indices List", "Polygon Indices", "polygonIndices")

        self.newOutput("Matrix List", "Transforms", "transforms")
        self.newOutput("Matrix List", "Inverted Transforms", "invertedTransforms")

    def draw(self, layout):
        if self.errorMessage != "":
            layout.label(self.errorMessage, icon = "ERROR")

    def execute(self, Vector3DList vertices, PolygonIndicesList polygons):
        self.errorMessage = ""
        if len(polygons) == 0 or polygons.getMaxIndex() < len(vertices):
            return extractPolygonTransforms(vertices, polygons, calcInverted = True)
        else:
            self.errorMessage = "Invalid polygon indices"
            return Matrix4x4List(), Matrix4x4List()

def extractPolygonTransforms(Vector3DList vertices, PolygonIndicesList polygons,
                             bint calcNormal = True, bint calcInverted = False):
    if not calcNormal and not calcInverted:
        return None

    cdef Py_ssize_t i
    cdef Vector3 center, normal, tangent, bitangent
    cdef Matrix4x4List transforms, invertedTransforms

    if calcNormal:
        transforms = Matrix4x4List(length = polygons.getLength())
    if calcInverted:
        invertedTransforms = Matrix4x4List(length = polygons.getLength())

    for i in range(transforms.length):
        extractPolygonData(
            vertices.data,
            polygons.indices.data + polygons.polyStarts.data[i],
            polygons.polyLengths.data[i],
            &center, &normal, &tangent)

        normalizeVec3_InPlace(&normal)
        normalizeVec3_InPlace(&tangent)
        crossVec3(&bitangent, &tangent, &normal)

        if calcNormal:
            createMatrix(transforms.data + i, &center, &normal, &tangent, &bitangent)
        if calcInverted:
            createInvertedMatrix(invertedTransforms.data + i, &center, &normal, &tangent, &bitangent)

    if calcNormal and calcInverted:
        return transforms, invertedTransforms
    elif calcNormal:
        return transforms
    else:
        return invertedTransforms

@cython.cdivision(True)
cdef void extractPolygonData(Vector3 *vertices,
                        unsigned int *indices, unsigned int vertexAmount,
                        Vector3 *center, Vector3 *normal, Vector3 *tangent):
    # Center
    cdef Py_ssize_t i
    cdef Vector3 *current
    cdef Vector3 sum = {"x" : 0, "y" : 0, "z" : 0}
    
    for i in range(vertexAmount):
        current = vertices + indices[i]
        sum.x += current.x
        sum.y += current.y
        sum.z += current.z
    scaleVec3(center, &sum, 1 / <float>vertexAmount)

    # Normal
    cdef Vector3 a, b
    subVec3(&a, vertices + indices[1], vertices + indices[0])
    subVec3(&b, vertices + indices[2], vertices + indices[0])
    crossVec3(normal, &a, &b)

    # Tangent
    tangent[0] = a

cdef void createMatrix(Matrix4 *m, Vector3 *center, Vector3 *normal, Vector3 *tangent, Vector3 *bitangent):
    m.a11, m.a12, m.a13, m.a14 = tangent.x, bitangent.x, normal.x, center.x
    m.a21, m.a22, m.a23, m.a24 = tangent.y, bitangent.y, normal.y, center.y
    m.a31, m.a32, m.a33, m.a34 = tangent.z, bitangent.z, normal.z, center.z
    m.a41, m.a42, m.a43, m.a44 = 0, 0, 0, 1

cdef void createInvertedMatrix(Matrix4 *m, Vector3 *center, Vector3 *normal, Vector3 *tangent, Vector3 *bitangent):
    m.a11, m.a12, m.a13 = tangent.x,   tangent.y,   tangent.z,
    m.a21, m.a22, m.a23 = bitangent.x, bitangent.y, bitangent.z
    m.a31, m.a32, m.a33 = normal.x,    normal.y,    normal.z
    m.a41, m.a42, m.a43, m.a44 = 0, 0, 0, 1

    m.a14 = -(tangent.x   * center.x + tangent.y   * center.y + tangent.z   * center.z)
    m.a24 = -(bitangent.x * center.x + bitangent.y * center.y + bitangent.z * center.z)
    m.a34 = -(normal.x    * center.x + normal.y    * center.y + normal.z    * center.z)
