# distutils: language = c++
# setup: options = c++11

from ... math cimport toVector3
from ... data_structures cimport Vector3DList, FloatList

cdef dict simdLevels = {
    0 : "Fallback",
    1 : "SSE2",
    2 : "SSE4.1",
    3 : "AVX2 & FMA3",
    4 : "AVX512",
    5 : "ARM NEON"
}

noiseTypesData = [
    ("SIMPLEX",     NoiseType.SimplexFractal, "Simplex",     0),
    ("PERLIN",      NoiseType.PerlinFractal,  "Perlin",      1),
    ("VALUE",       NoiseType.ValueFractal,   "Value",       2),
    ("CUBIC",       NoiseType.CubicFractal,   "Cubic",       3),
    ("CELLULAR",    NoiseType.Cellular,       "Cellular",    4),
    ("WHITE_NOISE", NoiseType.WhiteNoise,     "White Noise", 5)
]

cellularReturnTypesData = [
    ("CELL_VALUE",      CellularReturnType.CellValue,     "Cell Value",      0),
    ("DISTANCE",        CellularReturnType.Distance,      "Distance",        1),
    ("DISTANCE_2",      CellularReturnType.Distance2,     "Distance 2",      2),
    ("DISTANCE_2_ADD",  CellularReturnType.Distance2Add,  "Distance 2 Add",  3),
    ("DISTANCE_2_SUB",  CellularReturnType.Distance2Sub,  "Distance 2 Sub",  4),
    ("DISTANCE_2_MUL",  CellularReturnType.Distance2Mul,  "Distance 2 Mul",  5),
    ("DISTANCE_2_DIV",  CellularReturnType.Distance2Div,  "Distance 2 Div",  6),
    ("DISTANCE_2_CAVE", CellularReturnType.Distance2Cave, "Distance 2 Cave", 7),
    ("NOISE_LOOKUP",    CellularReturnType.NoiseLookup,   "Noise Lookup",    8)
]

cellularDistanceFunctionsData = [
    ("EUCLIDEAN", CellularDistanceFunction.Euclidean, "Euclidean", 0),
    ("MANHATTAN", CellularDistanceFunction.Manhattan, "Manhattan", 1),
    ("NATURAL",   CellularDistanceFunction.Natural,   "Natural",   2)
]

perturbTypesData = [
    ("NONE",               PerturbType.None,               "None",               0),
    ("GRADIENT",           PerturbType.Gradient,           "Gradient",           1),
    ("GRADIENT_FRACTAL",   PerturbType.GradientFractal,    "Gradient Fractal",   2),
    ("NORMALISE",          PerturbType.Normalise,          "Normalise",          3),
    ("GRADIENT_NORMALISE", PerturbType.Gradient_Normalise, "Gradient Normalise", 4),
    ("GRADIENT_FRACTAL_NORMALISE", PerturbType.GradientFractal_Normalise, "Gradient Fractal Normalise", 5)
]

fractalTypesData = [
    ("FBM",         FractalType.FBM,        "FBM",         0),
    ("BILLOW",      FractalType.Billow,     "Billow",      1),
    ("RIGID_MULTI", FractalType.RigidMulti, "Rigid Multi", 2)
]

cdef dict noiseTypes = {d[0] : d[1] for d in noiseTypesData}
cdef dict cellularReturnTypes = {d[0] : d[1] for d in cellularReturnTypesData}
cdef dict cellularDistanceFunctions = {d[0] : d[1] for d in cellularDistanceFunctionsData}
cdef dict perturbTypes = {d[0] : d[1] for d in perturbTypesData}
cdef dict fractalTypes = {d[0] : d[1] for d in fractalTypesData}

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

    def setAmplitude(self, float amplitude):
        self.amplitude = amplitude

    def setOffset(self, vector):
        self.offset = toVector3(vector)


    def calculateList(self, Vector3DList vectors not None):
        cdef FloatList result = FloatList(length = vectors.length)
        self.calculateList_LowLevel(vectors.data, vectors.length, result.data)
        return result

    cdef calculateList_LowLevel(self, Vector3 *vectors, Py_ssize_t amount, float *target):
        calcNoise(self, target, vectors, amount)

    def calculateSingle(self, vector):
        cdef Vector3 _vector = toVector3(vector)
        return self.calculateSingle_LowLevel(&_vector)

    cdef calculateSingle_LowLevel(self, Vector3 *vector):
        cdef float result
        calcNoise(self, &result, vector, 1)
        return result


cdef void calcNoise(PyNoise noise, float *results, Vector3 *vectors, Py_ssize_t amount):
    cdef FastNoiseVectorSet vectorSet
    vectorSet.SetSize(amount)
    vectorSet.sampleScale = 0

    cdef Py_ssize_t i
    for i in range(amount):
        vectorSet.xSet[i] = vectors[i].x
        vectorSet.ySet[i] = vectors[i].y
        vectorSet.zSet[i] = vectors[i].z

    cdef Vector3 offset = noise.offset
    noise.fn.FillNoiseSet(results, &vectorSet, offset.x, offset.y, offset.z)

    vectorSet.Free()

    cdef float amplitude = noise.amplitude
    for i in range(amount):
        results[i] *= amplitude
