import bpy
from bpy.props import *
from ... base_types.node import AnimationNode
from ... data_structures cimport Vector3DList, PolygonIndicesList, Matrix4x4List
from ... math cimport Vector3, setTranslationMatrix, scaleVec3, scaleVec3, toPyVector3

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
            return extractPolygonTransforms(vertices, polygons)
        else:
            self.errorMessage = "Invalid polygon indices"
            return Matrix4x4List(), Matrix4x4List()

def extractPolygonTransforms(Vector3DList vertices, PolygonIndicesList polygons):
    cdef:
        Matrix4x4List transforms = Matrix4x4List(length = polygons.getLength())
        Matrix4x4List invertedTransforms = Matrix4x4List(length = polygons.getLength())
        Vector3 center, invertedCenter
        long i, j
        long start, length

    for i in range(transforms.length):
        calcPolygonCenter(&center, vertices, polygons, i)
        setTranslationMatrix(transforms.data + i, &center)
        scaleVec3(&invertedCenter, &center, -1)
        setTranslationMatrix(invertedTransforms.data + i, &invertedCenter)

    return transforms, invertedTransforms

cdef calcPolygonCenter(Vector3* target, Vector3DList vertices, PolygonIndicesList polygons, long index):
    cdef:
        Vector3 sum
        Vector3* current
        long start = polygons.polyStarts.data[index]
        long length = polygons.polyLengths.data[index]
        long i
    sum.x = sum.y = sum.z = 0
    for i in range(length):
        current = vertices.data + polygons.indices.data[start + i]
        sum.x += current.x
        sum.y += current.y
        sum.z += current.z
    scaleVec3(target, &sum, 1 / <double>length)
