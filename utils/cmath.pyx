
cdef void addVec3(Vector3_t* target, Vector3_t* a, Vector3_t* b):
    target.x = a.x + b.x
    target.y = a.y + b.y
    target.z = a.z + b.z

cdef void transformVec3(Vector3_t* target, Vector3_t* v, Matrix4_t* m):
    cdef float newX, newY, newZ
    newX = v.x * m.a11 + v.y * m.a12 + v.z * m.a13 + m.a14
    newY = v.x * m.a21 + v.y * m.a22 + v.z * m.a23 + m.a24
    newZ = v.x * m.a31 + v.y * m.a32 + v.z * m.a33 + m.a34
    target.x = newX
    target.y = newY
    target.z = newZ

cdef void applyMatrix(Matrix4_t* m, value):
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
