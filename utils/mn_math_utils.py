from mn_utils import *
from mn_cache import *

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
	v1 = smoothedNoise(intX)
	v2 = smoothedNoise(intX + 1)
	v3 = smoothedNoise(intX + 2)
	v4 = smoothedNoise(intX + 3)
	return cubicInterpolation(v1, v2, v3, v4, x - intX)
	
def smoothedNoise(x):
	return smoothNoiseCache[x % smoothNoiseCacheSize]
	
def cubicInterpolation(v0, v1, v2, v3, x):
	p = v3 - v2 - v0 + v1
	return p * x**3 + ((v0 - v1) - p) * x**2 + (v2 - v0) * x + v1
	
	# P = (v3 - v2) - (v0 - v1)
	# Q = (v0 - v1) - P
	# R = v2 - v0
	# S = v1

	# return P*x**3 + Q*x**2 + R*x + S