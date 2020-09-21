import cython
from mathutils import Vector, noise
from ... algorithms.random import getRandom3DVector
from ... data_structures cimport DoubleList, Vector3DList
from ... math cimport Vector3, toVector3, scaleVec3_Inplace

# Blender Noise and Turbulance-Noise Functions.
def blNoise(str noiseBasis, Vector3DList vectors, Py_ssize_t seed, float amplitude, float frequency,
              axisScale, offset, bint normalization):
    cdef Py_ssize_t amount = vectors.length
    cdef DoubleList values = DoubleList(length = amount)
    cdef Vector3 newOffset = toVector3(offset + getRandom3DVector(seed, 10000))
    cdef Vector3 newAxisScale = toVector3(axisScale)
    cdef float value
    cdef Vector3 v
    cdef Py_ssize_t i
    for i in range(amount):
        v = vectorOffset(vectors.data[i], newAxisScale, newOffset, frequency)
        value = noise.noise(Vector((v.x, v.y, v.z)), noise_basis = noiseBasis)
        values.data[i] = amplitude * value
    if normalization:
        return normalizedNumbers(values)
    return values

def blTurbulence(str noiseBasis, Vector3DList vectors, Py_ssize_t seed, float amplitude, float frequency, axisScale,
                 offset, Py_ssize_t octaves, bint hard, float noiseAmplitude, float noiseFrequency, bint normalization):
    cdef Py_ssize_t amount = vectors.length
    cdef DoubleList values = DoubleList(length = amount)
    cdef Vector3 newOffset = toVector3(offset + getRandom3DVector(seed, 10000))
    cdef Vector3 newAxisScale = toVector3(axisScale)
    cdef float value
    cdef Vector3 v
    cdef Py_ssize_t i
    for i in range(amount):
        v = vectorOffset(vectors.data[i], newAxisScale, newOffset, frequency)
        value = noise.turbulence(Vector((v.x, v.y, v.z)), octaves, hard, noise_basis = noiseBasis,
                                 amplitude_scale = noiseAmplitude, frequency_scale = noiseFrequency)
        values.data[i] = amplitude * value
    if normalization:
        return normalizedNumbers(values)
    return values

# Blender Fractal Functions.
def blFractal(str noiseBasis, Vector3DList vectors, Py_ssize_t seed, float amplitude, float frequency,
              axisScale, offset, float hFactor, float lacunarity, Py_ssize_t octaves, bint normalization):
    cdef Py_ssize_t amount = vectors.length
    cdef DoubleList values = DoubleList(length = amount)
    cdef Vector3 newOffset = toVector3(offset + getRandom3DVector(seed, 10000))
    cdef Vector3 newAxisScale = toVector3(axisScale)
    cdef float value
    cdef Vector3 v
    cdef Py_ssize_t i
    for i in range(amount):
        v = vectorOffset(vectors.data[i], newAxisScale, newOffset, frequency)
        value = noise.fractal(Vector((v.x, v.y, v.z)), hFactor,
                              lacunarity, octaves, noise_basis = noiseBasis)
        values.data[i] = amplitude * value
    if normalization:
        return normalizedNumbers(values)
    return values

def blMultiFractal(str noiseBasis, Vector3DList vectors, Py_ssize_t seed, float amplitude, float frequency,
                   axisScale, offset, float hFactor, float lacunarity, Py_ssize_t octaves, bint normalization):
    cdef Py_ssize_t amount = vectors.length
    cdef DoubleList values = DoubleList(length = amount)
    cdef Vector3 newOffset = toVector3(offset + getRandom3DVector(seed, 10000))
    cdef Vector3 newAxisScale = toVector3(axisScale)
    cdef float value
    cdef Vector3 v
    cdef Py_ssize_t i
    for i in range(amount):
        v = vectorOffset(vectors.data[i], newAxisScale, newOffset, frequency)
        value = noise.multi_fractal(Vector((v.x, v.y, v.z)), hFactor,
                                    lacunarity, octaves, noise_basis = noiseBasis)
        values.data[i] = amplitude * value
    if normalization:
        return normalizedNumbers(values)
    return values

def blHeteroTerrain(str noiseBasis, Vector3DList vectors, Py_ssize_t seed, float amplitude, float frequency,
                    axisScale, offset, float hFactor, float lacunarity, Py_ssize_t octaves, float noiseOffset,
                    bint normalization):
    cdef Py_ssize_t amount = vectors.length
    cdef DoubleList values = DoubleList(length = amount)
    cdef Vector3 newOffset = toVector3(offset + getRandom3DVector(seed, 10000))
    cdef Vector3 newAxisScale = toVector3(axisScale)
    cdef float value
    cdef Vector3 v
    cdef Py_ssize_t i
    for i in range(amount):
        v = vectorOffset(vectors.data[i], newAxisScale, newOffset, frequency)
        value = noise.hetero_terrain(Vector((v.x, v.y, v.z)), hFactor,
                                     lacunarity, octaves, noiseOffset, noise_basis = noiseBasis)
        values.data[i] = amplitude * value
    if normalization:
        return normalizedNumbers(values)
    return values

def blRigidMultiFractal(str noiseBasis, Vector3DList vectors, Py_ssize_t seed, float amplitude, float frequency,
                        axisScale, offset, float hFactor, float lacunarity, Py_ssize_t octaves, float noiseOffset,
                        float gain, bint normalization):
    cdef Py_ssize_t amount = vectors.length
    cdef DoubleList values = DoubleList(length = amount)
    cdef Vector3 newOffset = toVector3(offset + getRandom3DVector(seed, 10000))
    cdef Vector3 newAxisScale = toVector3(axisScale)
    cdef float value
    cdef Vector3 v
    cdef Py_ssize_t i
    for i in range(amount):
        v = vectorOffset(vectors.data[i], newAxisScale, newOffset, frequency)
        value = noise.ridged_multi_fractal(Vector((v.x, v.y, v.z)), hFactor, lacunarity,
                                           octaves, noiseOffset, gain, noise_basis = noiseBasis)
        values.data[i] = amplitude * value
    if normalization:
        return normalizedNumbers(values)
    return values

def blHybridMultiFractal(str noiseBasis, Vector3DList vectors, Py_ssize_t seed, float amplitude, float frequency,
                         axisScale, offset, float hFactor, float lacunarity, Py_ssize_t octaves, float noiseOffset,
                         float gain, bint normalization):
    cdef Py_ssize_t amount = vectors.length
    cdef DoubleList values = DoubleList(length = amount)
    cdef Vector3 newOffset = toVector3(offset + getRandom3DVector(seed, 10000))
    cdef Vector3 newAxisScale = toVector3(axisScale)
    cdef float value
    cdef Vector3 v
    cdef Py_ssize_t i
    for i in range(amount):
        v = vectorOffset(vectors.data[i], newAxisScale, newOffset, frequency)
        value = noise.hybrid_multi_fractal(Vector((v.x, v.y, v.z)), hFactor, lacunarity,
                                           octaves, noiseOffset, gain, noise_basis = noiseBasis)
        values.data[i] = amplitude * value
    if normalization:
        return normalizedNumbers(values)
    return values

# Blender Variable Lacunarity Functions.
def blVariableLacunarity(str noiseBasis, str noiseBasis2, Vector3DList vectors, Py_ssize_t seed, float amplitude,float frequency,
                         axisScale, offset, float distortion, bint normalization):
    cdef Py_ssize_t amount = vectors.length
    cdef DoubleList values = DoubleList(length = amount)
    cdef Vector3 newOffset = toVector3(offset + getRandom3DVector(seed, 10000))
    cdef Vector3 newAxisScale = toVector3(axisScale)
    cdef float value
    cdef Vector3 v
    cdef Py_ssize_t i
    for i in range(amount):
        v = vectorOffset(vectors.data[i], newAxisScale, newOffset, frequency)
        value = noise.variable_lacunarity(Vector((v.x, v.y, v.z)), distortion, noise_type1 = noiseBasis,
                                          noise_type2 = noiseBasis2)
        values.data[i] = amplitude * value
    if normalization:
        return normalizedNumbers(values)
    return values

# Blender Noise-Vector and Turbulence-Vector Functions.
def blNoiseVector(str noiseBasis, Vector3DList vectors, Py_ssize_t seed, float amplitude, float frequency,
                  axisScale, offset, bint normalization):
    cdef Py_ssize_t amount = vectors.length
    cdef Vector3DList values = Vector3DList(length = amount)
    cdef Vector3 newOffset = toVector3(offset + getRandom3DVector(seed, 10000))
    cdef Vector3 newAxisScale = toVector3(axisScale)
    cdef Vector3 v, p
    cdef Py_ssize_t i
    for i in range(amount):
        v = vectorOffset(vectors.data[i], newAxisScale, newOffset, frequency)
        p = toVector3(noise.noise_vector(Vector((v.x, v.y, v.z)), noise_basis = noiseBasis))
        scaleVec3_Inplace(&p, amplitude)
        values.data[i] = p
    if normalization:
        return normalizedVectors(values)
    return values

def blTurbulenceVector(str noiseBasis, Vector3DList vectors, Py_ssize_t seed, float amplitude, float frequency, axisScale,
                 offset, Py_ssize_t octaves, bint hard, float noiseAmplitude, float noiseFrequency, bint normalization):
    cdef Py_ssize_t amount = vectors.length
    cdef Vector3DList values = Vector3DList(length = amount)
    cdef Vector3 newOffset = toVector3(offset + getRandom3DVector(seed, 10000))
    cdef Vector3 newAxisScale = toVector3(axisScale)
    cdef Vector3 v, p
    cdef Py_ssize_t i
    for i in range(amount):
        v = vectorOffset(vectors.data[i], newAxisScale, newOffset, frequency)
        p = toVector3(noise.turbulence_vector(Vector((v.x, v.y, v.z)), octaves, hard, noise_basis = noiseBasis,
                                              amplitude_scale = noiseAmplitude, frequency_scale = noiseFrequency))
        scaleVec3_Inplace(&p, amplitude)
        values.data[i] = p
    if normalization:
        return normalizedVectors(values)
    return values

cdef vectorOffset(Vector3 vector, Vector3 axisScale, Vector3 offset, float frequency):
    scaleVec3_Inplace(&axisScale, frequency)

    vector.x *= axisScale.x
    vector.y *= axisScale.y
    vector.z *= axisScale.z

    vector.x += offset.x
    vector.y += offset.y
    vector.z += offset.z
    return vector

@cython.cdivision(True)
cdef normalizedNumbers(DoubleList values):
    cdef Py_ssize_t amount = values.length
    cdef float avgValue = 0
    cdef Py_ssize_t i

    for i in range(amount):
        avgValue += values.data[i]
    avgValue /= amount

    for i in range(amount):
        values.data[i] -= avgValue

    return values

@cython.cdivision(True)
cdef normalizedVectors(Vector3DList vectors):
    cdef Py_ssize_t amount = vectors.length
    cdef Vector3 avgValue = toVector3((0, 0, 0))
    cdef Vector3 v
    cdef Py_ssize_t i

    for i in range(amount):
        v = vectors.data[i]
        avgValue.x += v.x
        avgValue.y += v.y
        avgValue.z += v.z
    scaleVec3_Inplace(&avgValue, 1.0 / amount)

    for i in range(amount):
        v = vectors.data[i]
        v.x -= avgValue.x
        v.y -= avgValue.y
        v.z -= avgValue.z
        vectors.data[i] = v
    return vectors
