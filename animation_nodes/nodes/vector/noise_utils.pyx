from mathutils import Vector, noise
from ... data_structures cimport DoubleList, Vector3DList

# Blender Fractal Functions:
def blFractal(str noiseBasis, Vector3DList vectors, float fractalDimension, float lacunarity,
            Py_ssize_t octaves):
    cdef Py_ssize_t amount = vectors.length
    cdef DoubleList values = DoubleList(length = amount)
    cdef Py_ssize_t i
    for i in range(amount):
        v = vectors.data[i]
        values.data[i] = noise.fractal(Vector((v.x, v.y, v.z)), fractalDimension,
                                       lacunarity, octaves, noise_basis = noiseBasis)
    return values

def blMultiFractal(str noiseBasis, Vector3DList vectors, float fractalDimension, float lacunarity,
                   Py_ssize_t octaves):
    cdef Py_ssize_t amount = vectors.length
    cdef DoubleList values = DoubleList(length = amount)
    cdef Py_ssize_t i
    for i in range(amount):
        v = vectors.data[i]
        values.data[i] = noise.multi_fractal(Vector((v.x, v.y, v.z)), fractalDimension, lacunarity,
                                             octaves, noise_basis = noiseBasis)
    return values

def blHeteroTerrain(str noiseBasis, Vector3DList vectors, float fractalDimension, float lacunarity,
                    Py_ssize_t octaves, float offset):
    cdef Py_ssize_t amount = vectors.length
    cdef DoubleList values = DoubleList(length = amount)
    cdef Py_ssize_t i
    for i in range(amount):
        v = vectors.data[i]
        values.data[i] = noise.hetero_terrain(Vector((v.x, v.y, v.z)), fractalDimension, lacunarity,
                                              octaves, offset, noise_basis = noiseBasis)
    return values

def blRigidMultiFractal(str noiseBasis, Vector3DList vectors, float fractalDimension, float lacunarity,
                        Py_ssize_t octaves, float offset, float gain):
    cdef Py_ssize_t amount = vectors.length
    cdef DoubleList values = DoubleList(length = amount)
    cdef Py_ssize_t i
    for i in range(amount):
        v = vectors.data[i]
        values.data[i] = noise.ridged_multi_fractal(Vector((v.x, v.y, v.z)), fractalDimension, lacunarity,
                                                    octaves, offset, gain, noise_basis = noiseBasis)
    return values

def blHybridMultiFractal(str noiseBasis, Vector3DList vectors, float fractalDimension, float lacunarity,
                         Py_ssize_t octaves, float offset, float gain):
    cdef Py_ssize_t amount = vectors.length
    cdef DoubleList values = DoubleList(length = amount)
    cdef Py_ssize_t i
    for i in range(amount):
        v = vectors.data[i]
        values.data[i] = noise.hybrid_multi_fractal(Vector((v.x, v.y, v.z)), fractalDimension, lacunarity,
                                                    octaves, offset, gain, noise_basis = noiseBasis)
    return values

# Blender Variable Lacunarity Functions:
def blVariableLacunarity(str noiseBasis, str noiseBasis2, Vector3DList vectors, float distortion):
    cdef Py_ssize_t amount = vectors.length
    cdef DoubleList values = DoubleList(length = amount)
    cdef Py_ssize_t i
    for i in range(amount):
        v = vectors.data[i]
        values.data[i] = noise.variable_lacunarity(Vector((v.x, v.y, v.z)), distortion, noise_type1 = noiseBasis,
                                                   noise_type2 = noiseBasis2)
    return values

# Blender Turbulence Functions:
def blTurbulence(str noiseBasis, Vector3DList vectors, int seed, Py_ssize_t octaves, bint hard, float amplitude, float frequency):
    cdef Py_ssize_t amount = vectors.length
    cdef Vector3DList values = Vector3DList(length = amount)
    cdef Py_ssize_t i
    noise.seed_set(seed)
    for i in range(amount):
        v = vectors.data[i]
        p = noise.turbulence_vector(Vector((v.x, v.y, v.z)), octaves, hard, noise_basis=noiseBasis,
                                    amplitude_scale = amplitude, frequency_scale = frequency)
        values.data[i].x = p[0]
        values.data[i].y = p[1]
        values.data[i].z = p[2]
    return values
