from libc.math cimport sqrt
from ... data_structures cimport QuaternionList

cdef float sin_45 = <float>(1.0 / sqrt(2.0))

# The particle rotations returned by Blender don't align with the actual rotations
# of the particles. This function corrects the rotations by shifting the quaternion
# components and rotating 90 degrees along the negative z axis.
def correctParticleRotations(QuaternionList rotations):
    cdef QuaternionList correctedRotations = QuaternionList(length = len(rotations))
    cdef Py_ssize_t i
    cdef float ws, xs, ys, zs
    for i in range(len(rotations)):
        ws = rotations.data[i].w * sin_45
        xs = rotations.data[i].x * sin_45
        ys = rotations.data[i].y * sin_45
        zs = rotations.data[i].z * sin_45
        correctedRotations.data[i].w = xs + ws
        correctedRotations.data[i].x = ys - zs
        correctedRotations.data[i].y = ys + zs
        correctedRotations.data[i].z = ws - xs
    return correctedRotations

