from .. mn_utils import *
from .. mn_cache import *
from mathutils import *

# perlin noise
################################

smoothNoiseCacheSize = 7919
smoothNoiseCache = []
for i in range(smoothNoiseCacheSize):
    smoothNoiseCache.append(getUniformRandom(i, -1, 1)/2.0 + getUniformRandom(i-1, -1, 1)/4.0 + getUniformRandom(i+1, -1, 1)/4.0)

def perlinNoise(x, persistance, octaves):
    total = 0
    for i in range(octaves):
        frequency = 2**i
        localAmplitude = persistance**i
        total += interpolatedNoise(x * frequency) * localAmplitude
    return total

def interpolatedNoise(x):
    intX = int(x)
    v1 = smoothNoiseCache[intX % smoothNoiseCacheSize]
    v2 = smoothNoiseCache[(intX+1) % smoothNoiseCacheSize]
    v3 = smoothNoiseCache[(intX+2) % smoothNoiseCacheSize]
    v4 = smoothNoiseCache[(intX+3) % smoothNoiseCacheSize]
    return cubicInterpolation(v1, v2, v3, v4, x - intX)
    
def cubicInterpolation(v0, v1, v2, v3, x):
    p = v3 - v2 - v0 + v1
    return p * x**3 + ((v0 - v1) - p) * x**2 + (v2 - v0) * x + v1
    
    # P = (v3 - v2) - (v0 - v1)
    # Q = (v0 - v1) - P
    # R = v2 - v0
    # S = v1

    # return P*x**3 + Q*x**2 + R*x + S
    
    
# matrices
###################################

def composeMatrix(location, rotation, scale):
    matrix = Matrix.Translation(location)
    matrix *= Matrix.Rotation(rotation[2], 4, 'Z')
    matrix *= Matrix.Rotation(rotation[1], 4, 'Y')
    matrix *= Matrix.Rotation(rotation[0], 4, 'X')
    matrix *= Matrix.Scale(scale[0], 4, [1, 0, 0])
    matrix *= Matrix.Scale(scale[1], 4, [0, 1, 0])
    matrix *= Matrix.Scale(scale[2], 4, [0, 0, 1])
    return matrix