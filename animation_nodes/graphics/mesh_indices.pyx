cimport cython

import bpy
import bgl
import blf
from .. utils.blender_ui import getDpi
from .. data_structures cimport Vector3DList
from .. math cimport Matrix4, Vector3, Vector4, multMatrix4AndVec4, toMatrix4

def drawVertexIndices_ObjectMode(object, color = (1, 1, 1), fontSize = 14):
    region = bpy.context.region
    cdef float width = region.width
    cdef float height = region.height

    cdef Py_ssize_t i
    cdef Vector3DList vertices = object.data.an.getVertices()
    cdef Matrix4 transformation = getTransformationMatrix(object)

    blf.size(0, fontSize, int(getDpi()))
    bgl.glColor3f(*color)
    for i in range(len(vertices)):
        drawAtPoint(vertices.data + i, str(i), &transformation, width, height)

cdef Matrix4 getTransformationMatrix(object) except *:
    viewMatrix = bpy.context.space_data.region_3d.perspective_matrix
    objectMatrix = object.matrix_world
    return toMatrix4(viewMatrix * objectMatrix)

blfDraw = blf.draw
blfPosition = blf.position

@cython.cdivision(True)
cdef drawAtPoint(Vector3 *center, str text,
                 Matrix4 *transformation, float width, float height):
    cdef Vector4 point, projected
    point = {"x" : center.x, "y" : center.y, "z" : center.z, "w" : 1}
    multMatrix4AndVec4(&projected, transformation, &point)
    if projected.w <= 0:
        return
    projected.x /= projected.w
    projected.y /= projected.w

    cdef int x, y
    x = <int>((1.0 + projected.x) * width / 2.0)
    y = <int>((1.0 + projected.y) * height / 2.0)

    blfPosition(0, x, y, 0)
    blfDraw(0, text)
