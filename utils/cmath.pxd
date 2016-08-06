cdef struct Vector3_t:
    float x, y, z

cdef struct Matrix4_t:
    float a11, a12, a13, a14
    float a21, a22, a23, a24
    float a31, a32, a33, a34
    float a41, a42, a43, a44

cdef void addVec3(Vector3_t* target, Vector3_t* a, Vector3_t* b)
cdef void transformVec3(Vector3_t* target, Vector3_t* v, Matrix4_t* m)
cdef void applyMatrix(Matrix4_t* m, value)
