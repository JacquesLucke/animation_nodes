from bgl import *
from .. data_structures cimport Vector3DList, Matrix4x4List
from .. math cimport Vector3, Matrix4
from .. math cimport transformVec3AsPoint_InPlace

# cdef object vertex3f = glVertex3f

def drawVector3DListPoints(Vector3DList vectors):
    cdef Py_ssize_t i
    glBegin(GL_POINTS)
    for i in range(len(vectors)):
        vertex3f(vectors.data[i].x,
                 vectors.data[i].y,
                 vectors.data[i].z)
    glEnd()

def drawMatrix4x4List(Matrix4x4List matrices, float scale, bint drawLetters):
    cdef Py_ssize_t i
    glBegin(GL_LINES)
    for i in range(len(matrices)):
        drawMatrixRepresentationLines(matrices.data + i, scale)
    if drawLetters:
        for i in range(len(matrices)):
            drawMatrixOrientationLetters(matrices.data + i, scale)
    glEnd()

cdef void drawMatrixRepresentationLines(Matrix4 *matrix, float s):
    drawTransformedPoint(matrix, {"x" : -s, "y" :  0, "z" :  0})
    drawTransformedPoint(matrix, {"x" :  s, "y" :  0, "z" :  0})
    drawTransformedPoint(matrix, {"x" :  0, "y" : -s, "z" :  0})
    drawTransformedPoint(matrix, {"x" :  0, "y" :  s, "z" :  0})
    drawTransformedPoint(matrix, {"x" :  0, "y" :  0, "z" : -s})
    drawTransformedPoint(matrix, {"x" :  0, "y" :  0, "z" :  s})

cdef void drawMatrixOrientationLetters(Matrix4 *matrix, float s):
    # X
    drawTransformedPoint(matrix, {"x" : s * 1.1, "y" : 0, "z" : s *  0.2})
    drawTransformedPoint(matrix, {"x" : s * 1.3, "y" : 0, "z" : s * -0.2})
    drawTransformedPoint(matrix, {"x" : s * 1.3, "y" : 0, "z" : s *  0.2})
    drawTransformedPoint(matrix, {"x" : s * 1.1, "y" : 0, "z" : s * -0.2})

    # Y
    drawTransformedPoint(matrix, {"x" : 0, "y" : s * 1.1, "z" : s * 0.2})
    drawTransformedPoint(matrix, {"x" : 0, "y" : s * 1.2, "z" : 0})
    drawTransformedPoint(matrix, {"x" : 0, "y" : s * 1.3, "z" : s *  0.2})
    drawTransformedPoint(matrix, {"x" : 0, "y" : s * 1.1, "z" : s * -0.2})

    # Z
    drawTransformedPoint(matrix, {"x" : s * -0.1, "y" : 0, "z" : s * 1.3})
    drawTransformedPoint(matrix, {"x" : s *  0.1, "y" : 0, "z" : s * 1.3})
    drawTransformedPoint(matrix, {"x" : s * -0.1, "y" : 0, "z" : s * 1.3})
    drawTransformedPoint(matrix, {"x" : s *  0.1, "y" : 0, "z" : s * 1.1})
    drawTransformedPoint(matrix, {"x" : s * -0.1, "y" : 0, "z" : s * 1.1})
    drawTransformedPoint(matrix, {"x" : s *  0.1, "y" : 0, "z" : s * 1.1})

cdef void drawTransformedPoint(Matrix4 *matrix, Vector3 point):
    transformVec3AsPoint_InPlace(&point, matrix)
    vertex3f(point.x, point.y, point.z)