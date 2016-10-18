from libc.math cimport atan2, sqrt

# Matrix to Euler
################################################################

def matrix4x4ListToEulerList(Matrix4x4List matrices):
    cdef EulerList rotations = EulerList(length = matrices.length)
    cdef long i
    for i in range(rotations.length):
        matrixToEuler(rotations.data + i, matrices.data + i)
    return rotations

cdef matrixToEuler(Euler3* target, Matrix3_or_Matrix4* m):
    target.order = 0
    target.x = atan2(m.a32, m.a33)
    target.y = atan2(-m.a31, sqrt(m.a32 * m.a32 + m.a33 * m.a33))
    target.z = atan2(m.a21, m.a11)
