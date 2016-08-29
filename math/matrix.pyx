cdef void transformVec3AsPoint_InPlace(Vector3* v, Matrix4* m):
    cdef float newX, newY, newZ
    newX = v.x * m.a11 + v.y * m.a12 + v.z * m.a13 + m.a14
    newY = v.x * m.a21 + v.y * m.a22 + v.z * m.a23 + m.a24
    newZ = v.x * m.a31 + v.y * m.a32 + v.z * m.a33 + m.a34
    v.x, v.y, v.z = newX, newY, newZ

cdef void transformVec3AsPoint(Vector3* target, Vector3* v, Matrix4* m):
    target.x = v.x * m.a11 + v.y * m.a12 + v.z * m.a13 + m.a14
    target.y = v.x * m.a21 + v.y * m.a22 + v.z * m.a23 + m.a24
    target.z = v.x * m.a31 + v.y * m.a32 + v.z * m.a33 + m.a34

cdef void transformVec3AsDirection_InPlace(Vector3* v, Matrix4* m):
    cdef float newX, newY, newZ
    newX = v.x * m.a11 + v.y * m.a12 + v.z * m.a13
    newY = v.x * m.a21 + v.y * m.a22 + v.z * m.a23
    newZ = v.x * m.a31 + v.y * m.a32 + v.z * m.a33
    v.x, v.y, v.z = newX, newY, newZ

cdef void transformVec3AsDirection(Vector3* target, Vector3* v, Matrix4* m):
    target.x = v.x * m.a11 + v.y * m.a12 + v.z * m.a13
    target.y = v.x * m.a21 + v.y * m.a22 + v.z * m.a23
    target.z = v.x * m.a31 + v.y * m.a32 + v.z * m.a33

cdef void setIdentityMatrix4(Matrix4* m):
    m.a12 = m.a13 = m.a14 = 0
    m.a21 = m.a23 = m.a24 = 0
    m.a31 = m.a32 = m.a34 = 0
    m.a41 = m.a42 = m.a43 = 0
    m.a11 = m.a22 = m.a33 = m.a44 = 1

cdef void setTranslationMatrix4(Matrix4* m, Vector3* v):
    m.a14, m.a24, m.a34 = v.x, v.y, v.z
    m.a11 = m.a22 = m.a33 = m.a44 = 1
    m.a12 = m.a13 = 0
    m.a21 = m.a23 = 0
    m.a31 = m.a32 = 0
    m.a41 = m.a42 = m.a43 = 0

cdef void setTranslationScaleMatrix4(Matrix4* m, Vector3* t, Vector3* s):
    m.a11, m.a22, m.a33 = s.x, s.y, s.z
    m.a14, m.a24, m.a34 = t.x, t.y, t.z
    m.a44 = 1
    m.a12 = m.a13 = 0
    m.a21 = m.a23 = 0
    m.a31 = m.a32 = 0
    m.a41 = m.a42 = m.a43 = 0

cdef void multMatrix4(Matrix4* target, Matrix4* x, Matrix4* y):
    target.a11 = x.a11 * y.a11  +  x.a12 * y.a21  +  x.a13 * y.a31  +  x.a14 * y.a41
    target.a12 = x.a11 * y.a12  +  x.a12 * y.a22  +  x.a13 * y.a32  +  x.a14 * y.a42
    target.a13 = x.a11 * y.a13  +  x.a12 * y.a23  +  x.a13 * y.a33  +  x.a14 * y.a43
    target.a14 = x.a11 * y.a14  +  x.a12 * y.a24  +  x.a13 * y.a34  +  x.a14 * y.a44

    target.a21 = x.a21 * y.a11  +  x.a22 * y.a21  +  x.a23 * y.a31  +  x.a24 * y.a41
    target.a22 = x.a21 * y.a12  +  x.a22 * y.a22  +  x.a23 * y.a32  +  x.a24 * y.a42
    target.a23 = x.a21 * y.a13  +  x.a22 * y.a23  +  x.a23 * y.a33  +  x.a24 * y.a43
    target.a24 = x.a21 * y.a14  +  x.a22 * y.a24  +  x.a23 * y.a34  +  x.a24 * y.a44

    target.a31 = x.a31 * y.a11  +  x.a32 * y.a21  +  x.a33 * y.a31  +  x.a34 * y.a41
    target.a32 = x.a31 * y.a12  +  x.a32 * y.a22  +  x.a33 * y.a32  +  x.a34 * y.a42
    target.a33 = x.a31 * y.a13  +  x.a32 * y.a23  +  x.a33 * y.a33  +  x.a34 * y.a43
    target.a34 = x.a31 * y.a14  +  x.a32 * y.a24  +  x.a33 * y.a34  +  x.a34 * y.a44

    target.a41 = x.a41 * y.a11  +  x.a42 * y.a21  +  x.a43 * y.a31  +  x.a44 * y.a41
    target.a42 = x.a41 * y.a12  +  x.a42 * y.a22  +  x.a43 * y.a32  +  x.a44 * y.a42
    target.a43 = x.a41 * y.a13  +  x.a42 * y.a23  +  x.a43 * y.a33  +  x.a44 * y.a43
    target.a44 = x.a41 * y.a14  +  x.a42 * y.a24  +  x.a43 * y.a34  +  x.a44 * y.a44
