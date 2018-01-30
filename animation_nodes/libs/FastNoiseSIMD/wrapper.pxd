from ... math cimport Vector3

cdef extern from "FastNoiseSIMD.h":
    cdef cppclass FastNoiseSIMD:

        @staticmethod
        FastNoiseSIMD *NewFastNoiseSIMD()
        @staticmethod
        int GetSIMDLevel()

        void SetSeed(int seed)
        void SetFrequency(float frequency)
        void SetAxisScales(float xScale, float yScale, float zScale)
        void SetFractalOctaves(int octaves)
        void SetNoiseType(NoiseType noiseType)

        void SetCellularJitter(float cellularJitter)
        void SetCellularNoiseLookupType(NoiseType noiseType)
        void SetCellularNoiseLookupFrequency(float frequency)
        void SetCellularDistanceFunction(CellularDistanceFunction function)
        void SetCellularReturnType(CellularReturnType cellularReturnType)

        void SetPerturbType(PerturbType perturbType)
        void SetPerturbFrequency(float frequency)

        void SetFractalType(FractalType fractalType)

        void FillNoiseSet(float *noiseSet, FastNoiseVectorSet *vectorSet, float xOffset, float yOffset, float zOffset)

    cdef struct FastNoiseVectorSet:
        int size
        float *xSet
        float *ySet
        float *zSet

        int sampleScale
        int sampleSizeX;
        int sampleSizeY;
        int sampleSizeZ;

        void SetSize(int size)
        void Free()


    enum NoiseType "FastNoiseSIMD::NoiseType":
        Value           "FastNoiseSIMD::Value"
        ValueFractal    "FastNoiseSIMD::ValueFractal"
        Perlin          "FastNoiseSIMD::Perlin"
        PerlinFractal   "FastNoiseSIMD::PerlinFractal"
        Simplex         "FastNoiseSIMD::Simplex"
        SimplexFractal  "FastNoiseSIMD::SimplexFractal"
        WhiteNoise      "FastNoiseSIMD::WhiteNoise"
        Cellular        "FastNoiseSIMD::Cellular"
        Cubic           "FastNoiseSIMD::Cubic"
        CubicFractal    "FastNoiseSIMD::CubicFractal"

    enum CellularReturnType "FastNoiseSIMD::CellularReturnType":
        CellValue       "FastNoiseSIMD::CellValue"
        Distance        "FastNoiseSIMD::Distance"
        Distance2       "FastNoiseSIMD::Distance2"
        Distance2Add    "FastNoiseSIMD::Distance2Add"
        Distance2Sub    "FastNoiseSIMD::Distance2Sub"
        Distance2Mul    "FastNoiseSIMD::Distance2Mul"
        Distance2Div    "FastNoiseSIMD::Distance2Div"
        NoiseLookup     "FastNoiseSIMD::NoiseLookup"
        Distance2Cave   "FastNoiseSIMD::Distance2Cave"

    enum CellularDistanceFunction "FastNoiseSIMD::CellularDistanceFunction":
        Euclidean   "FastNoiseSIMD::Euclidean"
        Manhattan   "FastNoiseSIMD::Manhattan"
        Natural     "FastNoiseSIMD::Natural"

    enum PerturbType "FastNoiseSIMD::PerturbType":
        None                        "FastNoiseSIMD::None"
        Gradient                    "FastNoiseSIMD::Gradient"
        GradientFractal             "FastNoiseSIMD::GradientFractal"
        Normalise                   "FastNoiseSIMD::Normalise"
        Gradient_Normalise          "FastNoiseSIMD::Gradient_Normalise"
        GradientFractal_Normalise   "FastNoiseSIMD::GradientFractal_Normalise"

    enum FractalType "FastNoiseSIMD::FractalType":
        FBM         "FastNoiseSIMD::FBM"
        Billow      "FastNoiseSIMD::Billow"
        RigidMulti  "FastNoiseSIMD::RigidMulti"


cdef class PyNoise:
    cdef FastNoiseSIMD *fn
    cdef Vector3 offset
    cdef float amplitude

    cdef calculateList_LowLevel(self, Vector3 *vectors, Py_ssize_t amount, float *target)
    cdef calculateSingle_LowLevel(self, Vector3 *vector)
