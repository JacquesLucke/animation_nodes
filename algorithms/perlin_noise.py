from . random import getUniformRandom

# setup a cache for faster results
smoothNoiseCacheSize = 17919
smoothNoiseCache = []
for i in range(smoothNoiseCacheSize):
    smoothNoiseCache.append(getUniformRandom(i, -1, 1)/2.0 + getUniformRandom(i-1, -1, 1)/4.0 + getUniformRandom(i+1, -1, 1)/4.0)

# http://freespace.virgin.net/hugo.elias/models/m_perlin.htm
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
