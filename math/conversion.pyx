from mathutils import Vector, Matrix, Euler

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


# Eulers
##########################################################

cdef Euler3 toEuler3(value) except *:
    cdef Euler3 e
    setEuler3(&e, value)
    return e

cdef setEuler3(Euler3* e, value):
    if not isinstance(value, Euler):
        raise TypeError("value is no mathutils.Euler object")
    e.x = value.x
    e.y = value.y
    e.z = value.z
    cdef str order = value.order
    if   order == "XYZ": e.order = 0
    elif order == "XZY": e.order = 1
    elif order == "YXZ": e.order = 2
    elif order == "YZX": e.order = 3
    elif order == "ZXY": e.order = 4
    elif order == "ZYX": e.order = 5

cdef toPyEuler3(Euler3* e):
    if e.order == 0: return Euler((e.x, e.y, e.z), "XYZ")
    if e.order == 1: return Euler((e.x, e.y, e.z), "XZY")
    if e.order == 2: return Euler((e.x, e.y, e.z), "YXZ")
    if e.order == 3: return Euler((e.x, e.y, e.z), "YZX")
    if e.order == 4: return Euler((e.x, e.y, e.z), "ZXY")
    if e.order == 5: return Euler((e.x, e.y, e.z), "ZYX")
