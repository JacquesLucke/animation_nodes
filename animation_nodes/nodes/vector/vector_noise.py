import bpy
from bpy.props import *
from . noise_utils import *
from mathutils import noise
from ... libs.FastNoiseSIMD import Noise3DNodeBase
from ... data_structures import DoubleList, Vector3DList
from ... base_types import AnimationNode, VectorizedSocket

noiseSelectItems = [
    ("FASTNOISE", "Fast Noise", "Use fast noises from SIMD", "", 0),
    ("BLENDERNOISE", "Blender Noise", "Use builtin Blender noises", "", 1)
]

blenderNoiseTypeItems = [
    ("NOISE", "Noise", "Blender Fractal Noise", "", 0),
    ("3DNOISE", "3D Noise", "Blender Vector Turbulence Noise", "", 1),
    ("VARIABLELACUNARITY", "Variable Lacunarity", "Blender Variable Lacunarity", "", 2),
    ("VORONOI", "Voronoi", "Blender Voronoi Noise", "", 3)
]

noiseModeItems = [
    ("FRACTAL", "Fractal", "", "", 0),
    ("MULTI_FRACTAL", "Multi Fractal", "", "", 1),
    ("HETERO_TERRAIN", "Hetero Terrain", "", "", 2),
    ("RIDGED_MULTI_FRACTAL", "Ridged Multi Fractal", "", "", 3),
    ("HYBRID_MULTI_FRACTAL", "Hybrid Multi Fractal", "", "", 4)
]

noiseBasisModeItems = [
    ("BLENDER", "Blender", "", "", 0),
    ("PERLIN_ORIGINAL", "Perlin Orginal", "", "", 1),
    ("PERLIN_NEW", "Perlin New", "", "", 2),
    ("VORONOI_F1", "Voronoi F1", "", "", 3),
    ("VORONOI_F2", "Voronoi F2", "", "", 4),
    ("VORONOI_F3", "Voronoi F3", "", "", 5),
    ("VORONOI_F4", "Voronoi F4", "", "", 6),
    ("VORONOI_F2F1", "Voronoi F2F1", "", "", 7),
    ("VORONOI_CRACKLE", "Voronoi Crackle", "", "", 8),
    ("CELLNOISE", "Cell Noise", "", "", 9)
]

noiseBasisModeItems2 = [
    ("BLENDER", "Blender", "", "", 0),
    ("PERLIN_ORIGINAL", "Perlin Orginal", "", "", 1),
    ("PERLIN_NEW", "Perlin New", "", "", 2),
    ("VORONOI_F1", "Voronoi F1", "", "", 3),
    ("VORONOI_F2", "Voronoi F2", "", "", 4),
    ("VORONOI_F3", "Voronoi F3", "", "", 5),
    ("VORONOI_F4", "Voronoi F4", "", "", 6),
    ("VORONOI_F2F1", "Voronoi F2F1", "", "", 7),
    ("VORONOI_CRACKLE", "Voronoi Crackle", "", "", 8),
    ("CELLNOISE", "Cell Noise", "", "", 9)
]

voronoiDistanceMetricItems = [
    ("DISTANCE", "Distance", "", "", 0),
    ("DISTANCE_SQUARED", "Distance Squared", "", "", 1),
    ("MANHATTAN", "Manhattan", "", "", 2),
    ("CHEBYCHEV", "Chebychev", "", "", 3),
    ("MINKOVSKY", "Minkovsky", "", "", 4),
    ("MINKOVSKY_HALF", "Minkovsky Half", "", "", 5),
    ("MINKOVSKY_FOUR", "Minkovsky Four", "", "", 6)
]

class VectorNoiseNode(bpy.types.Node, AnimationNode, Noise3DNodeBase):
    bl_idname = "an_VectorNoiseNode"
    bl_label = "Vector Noise"
    bl_width_default = 160

    noiseSelect = EnumProperty(name = "Type", default = "FASTNOISE",
        items = noiseSelectItems, update = AnimationNode.refresh)

    blenderNoiseType = EnumProperty(name = "Type", default = "NOISE",
        description = "Blender noise type",
        items = blenderNoiseTypeItems, update = AnimationNode.refresh)

    noiseMode = EnumProperty(name = "Mode", default = "FRACTAL",
        description = "Blender noise mode",
        items = noiseModeItems, update = AnimationNode.refresh)

    noiseBasis = EnumProperty(name = "Basis", default = "BLENDER",
        description = "Noise basis type",
        items = noiseBasisModeItems, update = AnimationNode.refresh)

    noiseBasis2 = EnumProperty(name = "Basis", default = "PERLIN_ORIGINAL",
        description = "Noise basis type",
        items = noiseBasisModeItems2, update = AnimationNode.refresh)

    voronoiDistanceMetric = EnumProperty(name = "Mode", default = "DISTANCE",
        description = "Voronoi distance metric modes",
        items = voronoiDistanceMetricItems, update = AnimationNode.refresh)        

    useVectorList: VectorizedSocket.newProperty()                

    def create(self):
        if self.noiseSelect == "FASTNOISE":
            self.newInput("Vector List", "Vectors", "vectors")
            self.createNoiseInputs()
            self.newOutput("Float List", "Value", "value")

        elif self.noiseSelect == "BLENDERNOISE":
            if self.blenderNoiseType == "NOISE":
                self.newInput(VectorizedSocket("Vector", "useVectorList",
                    ("Vector", "vector"), ("Vectors", "vectors"))) 
                self.newInput("Float", "Fractal Dimension", "fractalDimension")
                self.newInput("Float", "Lacunarity", "lacunarity")
                self.newInput("Integer", "Octaves", "octaves", value = 2, minValue = 1)
                if self.noiseMode == "HETERO_TERRAIN":
                    self.newInput("Float", "Offset", "offset")
                if self.noiseMode in ["RIDGED_MULTI_FRACTAL", "HYBRID_MULTI_FRACTAL"]:
                    self.newInput("Float", "Offset", "offset")
                    self.newInput("Float", "Gain", "gain")
                self.newOutput(VectorizedSocket("Float", "useVectorList",
                    ("Value", "value"), ("Values", "values")))

            elif self.blenderNoiseType == "3DNOISE":
                self.newInput(VectorizedSocket("Vector", "useVectorList",
                    ("Vector", "vector"), ("Vectors", "vectors")))
                self.newInput("Integer", "Seed", "seed")    
                self.newInput("Integer", "Octaves", "octaves", value = 2, minValue = 1)
                self.newInput("Boolean", "Hard", "hard", value = 0)
                self.newInput("Float", "Amplitude", "amplitude", value = 0.5)
                self.newInput("Float", "Frequency", "frequency", value = 2.5)
                self.newOutput(VectorizedSocket("Vector", "useVectorList",
                    ("Value", "value"), ("Values", "values")))

            elif self.blenderNoiseType == "VARIABLELACUNARITY":
                self.newInput(VectorizedSocket("Vector", "useVectorList",
                    ("Vector", "vector"), ("Vectors", "vectors")))    
                self.newInput("Float", "Distortion", "distortion")
                self.newOutput(VectorizedSocket("Float", "useVectorList",
                    ("Value", "value"), ("Values", "values")))

            elif self.blenderNoiseType == "VORONOI":
                self.newInput("Vector", "Vector", "vector")
                self.newInput("Float", "Exponent", "exponent", value = 2.5)
                self.newOutput("Float", "Distance 1","distance1")
                self.newOutput("Float", "Distance 2","distance2")
                self.newOutput("Float", "Distance 3","distance3")
                self.newOutput("Float", "Distance 4","distance4")
                self.newOutput("Vector", "Point 1","point1")
                self.newOutput("Vector", "Point 2","point2")
                self.newOutput("Vector", "Point 3","point3")
                self.newOutput("Vector", "Point 4","point4")        

    def draw(self, layout):
        layout.prop(self, "noiseSelect")
        if self.noiseSelect == "FASTNOISE":
            self.drawNoiseSettings(layout)
        else:
            if self.blenderNoiseType == "NOISE":
                layout.prop(self, "noiseMode", text = "")
                layout.prop(self, "noiseBasis", text = "")
            elif self.blenderNoiseType == "3DNOISE":
                layout.prop(self, "noiseBasis", text = "")
            elif self.blenderNoiseType == "VARIABLELACUNARITY":
                layout.prop(self, "noiseBasis", text = "")
                layout.prop(self, "noiseBasis2", text = "")
            elif self.blenderNoiseType == "VORONOI":
                layout.prop(self, "voronoiDistanceMetric", text = "")    

    def drawAdvanced(self, layout):
        if self.noiseSelect == "FASTNOISE":
            self.drawAdvancedNoiseSettings(layout)
        else:
            layout.prop(self, "blenderNoiseType")

    def getExecutionFunctionName(self):
        if self.noiseSelect == "FASTNOISE":
            return "execute_FastNoise"
        else:
            if self.blenderNoiseType == "NOISE":
                if self.noiseMode == "FRACTAL":
                    return "execute_Fractal"
                elif self.noiseMode == "MULTI_FRACTAL":
                    return "execute_MultiFractal"
                elif self.noiseMode == "HETERO_TERRAIN":
                    return "execute_HeteroTerrain"
                elif self.noiseMode == "RIDGED_MULTI_FRACTAL":
                    return "execute_RigidMultiFractal"
                elif self.noiseMode == "HYBRID_MULTI_FRACTAL":
                    return "execute_HybridMultiFractal"
            elif self.blenderNoiseType == "3DNOISE":
                return "execute_3dNoise"
            elif self.blenderNoiseType == "VARIABLELACUNARITY":
                return "execute_VariableLacunarity"
            elif self.blenderNoiseType == "VORONOI":
                return "execute_Voronoi"    

    def execute_FastNoise(self, vectors, *settings):
        noise = self.calculateNoise(vectors, *settings)
        return DoubleList.fromValues(noise)

    # Fractal Noise Methods:
    def execute_Fractal(self, vectors, fractalDimension, lacunarity, octaves):
        if not self.useVectorList: vectors = Vector3DList.fromValue(vectors)
        noiseBasis = self.noiseBasis
        values = blFractal(noiseBasis, vectors, fractalDimension, lacunarity, octaves)
        return self.valuesOut(values)    

    def execute_MultiFractal(self, vectors, fractalDimension, lacunarity, octaves):
        if not self.useVectorList: vectors = Vector3DList.fromValue(vectors)
        noiseBasis = self.noiseBasis
        values = blMultiFractal(noiseBasis, vectors, fractalDimension, lacunarity, octaves)
        return self.valuesOut(values)

    def execute_HeteroTerrain(self, vectors, fractalDimension, lacunarity, octaves, offset):
        if not self.useVectorList: vectors = Vector3DList.fromValue(vectors)
        noiseBasis = self.noiseBasis
        values = blHeteroTerrain(noiseBasis, vectors, fractalDimension, lacunarity, octaves, offset)
        return self.valuesOut(values)

    def execute_RigidMultiFractal(self, vectors, fractalDimension, lacunarity, octaves, offset, gain):
        if not self.useVectorList: vectors = Vector3DList.fromValue(vectors)
        noiseBasis = self.noiseBasis
        values = blRigidMultiFractal(noiseBasis, vectors, fractalDimension, lacunarity, octaves, offset, gain)
        return self.valuesOut(values)

    def execute_HybridMultiFractal(self, vectors, fractalDimension, lacunarity, octaves, offset, gain):
        if not self.useVectorList: vectors = Vector3DList.fromValue(vectors)           
        noiseBasis = self.noiseBasis
        values = blHybridMultiFractal(noiseBasis, vectors, fractalDimension, lacunarity, octaves, offset, gain)
        return self.valuesOut(values) 

    # 3D Noise Methods:
    def execute_3dNoise(self, vectors, seed, octaves, hard, amplitude, frequency):
        if not self.useVectorList: vectors = Vector3DList.fromValue(vectors)
        seed = max(seed, 1) 
        noiseBasis = self.noiseBasis
        values = blTurbulence(noiseBasis, vectors, seed, octaves, hard, amplitude, frequency)
        return self.valuesOut(values)

    # Variable Lacunarity Methods:
    def execute_VariableLacunarity(self, vectors, distortion):
        if not self.useVectorList: vectors = Vector3DList.fromValue(vectors)
        noiseBasis = self.noiseBasis
        noiseBasis2 = self.noiseBasis2
        values = blVariableLacunarity(noiseBasis, noiseBasis2, vectors, distortion)
        return self.valuesOut(values) 

    # Voronoi Methods:
    def execute_Voronoi(self, vector, exponent):
        voronoiDistanceMetric = self.voronoiDistanceMetric
        out = noise.voronoi(vector, distance_metric=voronoiDistanceMetric, exponent=exponent)
        distances = out[0]
        points = out[1]
        return distances[0],distances[1],distances[2],distances[3],points[0],points[1],points[2],points[3]

    def valuesOut(self, values):
        if not self.useVectorList:
            return values[0]
        else:
            return values                             
