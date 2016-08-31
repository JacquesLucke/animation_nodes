from mathutils import Vector, Matrix

# Vectors
##########################################################

cdef Vector3 toVector3(value) except *:
    cdef Vector3 v
    setVector3(&v, value)
    return v

cdef setVector3(Vector3* v, value):
    if len(value) != 3:
        raise TypeError("element is not a 3D vector")
    v.x = value[0]
    v.y = value[1]
    v.z = value[2]

cdef toPyVector3(Vector3* v):
    return Vector((v.x, v.y, v.z))


# Matrices
##########################################################

cdef Matrix4 toMatrix4(value) except *:
    cdef Matrix4 m
    setMatrix4(&m, value)
    return m

cdef setMatrix4(Matrix4* m, value):
    if not (len(value.row) == len(value.col) == 4):
        raise TypeError("element is not a 4x4 matrix")
    m.a11 = value[0][0]
    m.a12 = value[0][1]
    m.a13 = value[0][2]
    m.a14 = value[0][3]

    m.a21 = value[1][0]
    m.a22 = value[1][1]
    m.a23 = value[1][2]
    m.a24 = value[1][3]

    m.a31 = value[2][0]
    m.a32 = value[2][1]
    m.a33 = value[2][2]
    m.a34 = value[2][3]

    m.a41 = value[3][0]
    m.a42 = value[3][1]
    m.a43 = value[3][2]
    m.a44 = value[3][3]

cdef toPyMatrix4(Matrix4* m):
    return Matrix(((m.a11, m.a12, m.a13, m.a14),
                   (m.a21, m.a22, m.a23, m.a24),
                   (m.a31, m.a32, m.a33, m.a34),
                   (m.a41, m.a42, m.a43, m.a44)))
