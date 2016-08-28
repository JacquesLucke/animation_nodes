cdef void transformVec3_InPlace(Vector3* v, Matrix4* m):
    cdef float newX, newY, newZ
    newX = v.x * m.a11 + v.y * m.a12 + v.z * m.a13 + m.a14
    newY = v.x * m.a21 + v.y * m.a22 + v.z * m.a23 + m.a24
    newZ = v.x * m.a31 + v.y * m.a32 + v.z * m.a33 + m.a34
    v.x = newX
    v.y = newY
    v.z = newZ

cdef void transformVec3(Vector3* target, Vector3* v, Matrix4* m):
    target.x = v.x * m.a11 + v.y * m.a12 + v.z * m.a13 + m.a14
    target.y = v.x * m.a21 + v.y * m.a22 + v.z * m.a23 + m.a24
    target.z = v.x * m.a31 + v.y * m.a32 + v.z * m.a33 + m.a34
