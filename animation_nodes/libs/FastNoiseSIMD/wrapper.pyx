# distutils: language = c++

from ... math cimport Vector3, toVector3
from ... data_structures cimport Vector3DList, FloatList

cdef dict simdLevels = {
    0 : "Fallback",
    1 : "SSE2",
    2 : "SSE4.1",
    3 : "AVX2 & FMA3",
    4 : "AVX512",
    5 : "ARM NEON"
}

cdef dict noiseTypes = {
    "VALUE" :           NoiseType.ValueFractal,
    "PERLIN" :          NoiseType.PerlinFractal,
    "SIMPLEX" :         NoiseType.SimplexFractal,
    "WHITE_NOISE" :     NoiseType.WhiteNoise,
    "CELLULAR" :        NoiseType.Cellular,
    "CUBIC" :           NoiseType.CubicFractal
}

cdef dict cellularReturnTypes = {
    "CELL_VALUE" :      CellularReturnType.CellValue,
    "DISTANCE" :        CellularReturnType.Distance,
    "DISTANCE_2" :      CellularReturnType.Distance2,
    "DISTANCE_2_ADD" :  CellularReturnType.Distance2Add,
    "DISTANCE_2_SUB" :  CellularReturnType.Distance2Sub,
    "DISTANCE_2_MUL" :  CellularReturnType.Distance2Mul,
    "DISTANCE_2_DIV" :  CellularReturnType.Distance2Div,
    "DISTANCE_2_CAVE" : CellularReturnType.Distance2Cave,
    "NOISE_LOOKUP" :    CellularReturnType.NoiseLookup
}

cdef dict cellularDistanceFunctions = {
    "EUCLIDEAN" : CellularDistanceFunction.Euclidean,
    "MANHATTAN" : CellularDistanceFunction.Manhattan,
    "NATURAL" :   CellularDistanceFunction.Natural
}

cdef dict perturbTypes = {
    "NONE" :                       PerturbType.None,
    "GRADIENT" :                   PerturbType.Gradient,
    "GRADIENT_FRACTAL" :           PerturbType.GradientFractal,
    "NORMALISE" :                  PerturbType.Normalise,
    "GRADIENT_NORMALISE" :         PerturbType.Gradient_Normalise,
    "GRADIENT_FRACTAL_NORMALISE" : PerturbType.GradientFractal_Normalise
}

cdef dict fractalTypes = {
    "FBM" :         FractalType.FBM,
    "BILLOW" :      FractalType.Billow,
    "RIGID_MULTI" : FractalType.RigidMulti
}

noiseTypesList = list(sorted(noiseTypes.keys()))
cellularReturnTypesList = list(sorted(cellularReturnTypes.keys()))
cellularDistanceFunctionsList = list(sorted(cellularDistanceFunctions.keys()))
perturbTypesList = list(sorted(perturbTypes.keys()))
fractalTypesList = list(sorted(fractalTypes.keys()))

cdef class PyNoise:
    def __cinit__(self):
        self.fn = FastNoiseSIMD.NewFastNoiseSIMD()

    def __dealloc__(self):
        del self.fn

    def getSIMDLevelName(self):
        cdef int level = self.fn.GetSIMDLevel()
        return simdLevels[level]

    def setSeed(self, int seed):
        self.fn.SetSeed(seed)

    def setFrequency(self, float frequency):
        self.fn.SetFrequency(frequency)

    def setAxisScales(self, scales):
        self.fn.SetAxisScales(scales[0], scales[1], scales[2])

    def setNoiseType(self, str t):
        self.fn.SetNoiseType(noiseTypes[t])

    def setCellularReturnType(self, str t):
        self.fn.SetCellularReturnType(cellularReturnTypes[t])

    def setCellularJitter(self, float jitter):
        self.fn.SetCellularJitter(jitter)

    def setCellularNoiseLookupType(self, str t):
        self.fn.SetCellularNoiseLookupType(noiseTypes[t])

    def setCellularNoiseLookupFrequency(self, float frequency):
        print(frequency)
        self.fn.SetCellularNoiseLookupFrequency(frequency)

    def setCellularDistanceFunction(self, str t):
        self.fn.SetCellularDistanceFunction(cellularDistanceFunctions[t])

    def setPerturbType(self, str t):
        self.fn.SetPerturbType(perturbTypes[t])

    def setPerturbFrequency(self, float frequency):
        self.fn.SetPerturbFrequency(frequency)

    def setFractalType(self, str t):
        self.fn.SetFractalType(fractalTypes[t])

    def setOctaves(self, int octaves):
        if 1 <= octaves <= 10:
            self.fn.SetFractalOctaves(octaves)
        else:
            raise ValueError("octaves has to be between 1 and 10")


    def calculateList(self, Vector3DList vectors not None, float amplitude, offset = (0, 0, 0)):
        cdef Vector3 _offset = toVector3(offset)
        cdef FloatList result = FloatList(length = vectors.length)
        calcNoise(self, result.data, vectors.data, &_offset, amplitude, vectors.length)
        return result

    def calculateSingle(self, vector):
        cdef Vector3 _vector = toVector3(vector)
        cdef Vector3 offset = Vector3(0, 0, 0)
        cdef float result
        calcNoise(self, &result, &_vector, &offset, 1, 1)
        return result


cdef void calcNoise(PyNoise noise, float *results, Vector3 *vectors, Vector3 *offset, float amplitude, Py_ssize_t amount):
    cdef FastNoiseVectorSet vectorSet
    vectorSet.SetSize(amount)
    vectorSet.sampleScale = 0

    cdef Py_ssize_t i
    for i in range(amount):
        vectorSet.xSet[i] = vectors[i].x
        vectorSet.ySet[i] = vectors[i].y
        vectorSet.zSet[i] = vectors[i].z

    noise.fn.FillNoiseSet(results, &vectorSet, offset.x, offset.y, offset.z)

    vectorSet.Free()

    for i in range(amount):
        results[i] *= amplitude
