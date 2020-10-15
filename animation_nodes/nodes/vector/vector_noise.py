import bpy
from bpy.props import *
from mathutils import noise
from ... data_structures import DoubleList
from ... libs.FastNoiseSIMD import Noise3DNodeBase
from ... base_types import AnimationNode, VectorizedSocket
from . noise_utils import (
    blNoise,
    blTurbulence,
    blFractal,
    blMultiFractal,
    blHeteroTerrain,
    blRigidMultiFractal,
    blHybridMultiFractal,
    blVariableLacunarity,
    blNoiseVector,
    blTurbulenceVector
)

noiseSelectItems = [
    ("FASTNOISE", "Fast Noises", "Use fast noises from SIMD", "", 0),
    ("BLENDERNOISE", "Blender Noises", "Use builtin Blender noises", "", 1)
]

blenderNoiseTypeItems = [
    ("NOISE", "Noise", "Blender Fractal Noise", "", 0),
    ("3DNOISE", "3D Noise", "Blender Vector Turbulence Noise", "", 1),
    ("VARIABLELACUNARITY", "Mix Noise", "Blender Variable Lacunarity Noise", "", 2),
]

noiseModeItems = [
    ("NOISE", "Noise", "", "", 0),
    ("TURBULENCE", "Turbulence", "", "", 1),
    ("FRACTAL", "Fractal", "", "", 2),
    ("MULTI_FRACTAL", "Multi Fractal", "", "", 3),
    ("HETERO_TERRAIN", "Hetero Terrain", "", "", 4),
    ("RIDGED_MULTI_FRACTAL", "Ridged Multi Fractal", "", "", 5),
    ("HYBRID_MULTI_FRACTAL", "Hybrid Multi Fractal", "", "", 6)
]

noiseVectorModeItems = [
    ("NOISE", "Noise", "", "", 0),
    ("TURBULENCE", "Turbulence", "", "", 1)
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

class VectorNoiseNode(bpy.types.Node, AnimationNode, Noise3DNodeBase):
    bl_idname = "an_VectorNoiseNode"
    bl_label = "Vector Noise"
    bl_width_default = 160

    noiseSelect: EnumProperty(name = "Type", default = "FASTNOISE",
        items = noiseSelectItems, update = AnimationNode.refresh)

    blenderNoiseType: EnumProperty(name = "Type", default = "NOISE",
        description = "Blender noise type",
        items = blenderNoiseTypeItems, update = AnimationNode.refresh)

    noiseMode: EnumProperty(name = "Mode", default = "NOISE",
        description = "Blender noise mode",
        items = noiseModeItems, update = AnimationNode.refresh)

    noiseVectorMode: EnumProperty(name = "Mode", default = "NOISE",
        description = "Blender 3d noise mode",
        items = noiseVectorModeItems, update = AnimationNode.refresh)

    noiseBasis: EnumProperty(name = "Basis", default = "PERLIN_ORIGINAL",
        description = "Noise basis type",
        items = noiseBasisModeItems, update = AnimationNode.refresh)

    noiseBasis2: EnumProperty(name = "Basis", default = "BLENDER",
        description = "Noise basis type",
        items = noiseBasisModeItems2, update = AnimationNode.refresh)

    normalization: BoolProperty(name = "Normalized Noise Output", default = True,
        update = AnimationNode.refresh)

    def create(self):
        if self.noiseSelect == "FASTNOISE":
            self.newInput("Vector List", "Vectors", "vectors")
            self.createNoiseInputs()

            self.newOutput("Float List", "Values", "values")

        elif self.noiseSelect == "BLENDERNOISE":
            if self.blenderNoiseType == "NOISE":
                self.newInput("Vector List", "Vectors", "vectors")
                self.newInput("Integer", "Seed", "seed")
                self.newInput("Float", "Amplitude", "amplitude", value = 0.1)
                self.newInput("Float", "Frequency", "frequency", value = 1.0)
                self.newInput("Vector", "Axis Scale", "axisScale", value = (1, 1, 1), hide = True)
                self.newInput("Vector", "Offset", "offset")
                if self.noiseMode not in ["NOISE", "TURBULENCE"]:
                    self.newInput("Integer", "Octaves", "octaves", value = 3, minValue = 1)
                    self.newInput("Float", "H Factor", "hFactor", hide = True)
                    self.newInput("Float", "Lacunarity", "lacunarity", value = 0.1, hide = True)
                    if self.noiseMode == "HETERO_TERRAIN":
                        self.newInput("Float", "Noise Offset", "noiseOffset", hide = True)
                    if self.noiseMode in ["RIDGED_MULTI_FRACTAL", "HYBRID_MULTI_FRACTAL"]:
                        self.newInput("Float", "Noise Offset", "noiseOffset", hide = True)
                        self.newInput("Float", "Noise Gain", "noiseGain", hide = True)
                if self.noiseMode == "TURBULENCE":
                    self.newInput("Integer", "Octaves", "octaves", value = 2, minValue = 1)
                    self.newInput("Boolean", "Hard", "hard", value = False, hide = True)
                    self.newInput("Float", "Scale", "noiseAmplitude", value = 0.5, hide = True)
                    self.newInput("Float", "Detail", "noiseFrequency", value = 2.5, hide = True)

                self.newOutput("Float List", "Values", "values")

            elif self.blenderNoiseType == "3DNOISE":
                self.newInput("Vector List", "Vectors", "vectors")
                self.newInput("Integer", "Seed", "seed")
                self.newInput("Float", "Amplitude", "amplitude", value = 0.1)
                self.newInput("Float", "Frequency", "frequency", value = 1.0)
                self.newInput("Vector", "Axis Scale", "axisScale", value = (1, 1, 1), hide = True)
                self.newInput("Vector", "Offset", "offset")
                if self.noiseVectorMode == "TURBULENCE":
                    self.newInput("Integer", "Octaves", "octaves", value = 3, minValue = 1)
                    self.newInput("Boolean", "Hard", "hard", value = False, hide = True)
                    self.newInput("Float", "Scale", "noiseAmplitude", value = 0.5, hide = True)
                    self.newInput("Float", "Detail", "noiseFrequency", value = 2.5, hide = True)

                self.newOutput("Vector List", "Values", "values")

            elif self.blenderNoiseType == "VARIABLELACUNARITY":
                self.newInput("Vector List", "Vectors", "vectors")
                self.newInput("Integer", "Seed", "seed")
                self.newInput("Float", "Amplitude", "amplitude", value = 0.1)
                self.newInput("Float", "Frequency", "frequency", value = 1.0)
                self.newInput("Vector", "Axis Scale", "axisScale", value = (1, 1, 1), hide = True)
                self.newInput("Vector", "Offset", "offset")
                self.newInput("Float", "Distortion", "distortion", value = 0.2)

                self.newOutput("Float List", "Values", "values")

    def draw(self, layout):
        layout.prop(self, "noiseSelect", text = "")
        if self.noiseSelect == "FASTNOISE":
            self.drawNoiseSettings(layout)
        else:
            if self.blenderNoiseType == "NOISE":
                layout.prop(self, "noiseMode", text = "")
                layout.prop(self, "noiseBasis", text = "")
            elif self.blenderNoiseType == "3DNOISE":
                layout.prop(self, "noiseVectorMode", text = "")
                layout.prop(self, "noiseBasis", text = "")
            elif self.blenderNoiseType == "VARIABLELACUNARITY":
                layout.prop(self, "noiseBasis", text = "")
                layout.prop(self, "noiseBasis2", text = "")

    def drawAdvanced(self, layout):
        if self.noiseSelect == "FASTNOISE":
            self.drawAdvancedNoiseSettings(layout)
        else:
            layout.prop(self, "blenderNoiseType")
            layout.prop(self, "normalization")

            if self.blenderNoiseType == "NOISE" and self.noiseMode != "NOISE":
                box = layout.box()
                col = box.column(align = True)
                col.label(text = "Info", icon = "INFO")
                if self.noiseMode == "TURBULENCE":
                    col.label(text = "Hard - ON Sharp transitions, OFF Smooth transitions.")
                    col.label(text = "Scale - Amplitude of details.")
                    col.label(text = "Detail - Frequency of details.")
                else:
                    col.label(text = "Lacunarity - The gap between successive frequencies.")
                    if self.noiseMode in ["FRACTAL", "MULTI_FRACTAL"]:
                        col.label(text = "'H' Factor - The fractal increment factor.")
                    if self.noiseMode in ["HETERO_TERRAIN", "RIDGED_MULTI_FRACTAL", "HYBRID_MULTI_FRACTAL"]:
                        col.label(text = "'H' Factor - The fractal dimension of the roughest areas.")
                        col.label(text = "Noise 'Offset' - The height of the terrain above 'sea level'.")
                    if self.noiseMode in ["RIDGED_MULTI_FRACTAL", "HYBRID_MULTI_FRACTAL"]:
                        col.label(text = "Noise 'Gain' - Scaling applied to the values.")

            if self.noiseVectorMode == "TURBULENCE":
                box = layout.box()
                col = box.column(align = True)
                col.label(text = "Info", icon = "INFO")
                col.label(text = "Hard - ON: sharp transitions, OFF: smooth transitions.")
                col.label(text = "Scale - Amplitude of details.")
                col.label(text = "Detail - Frequency of details.")

    def getExecutionFunctionName(self):
        if self.noiseSelect == "FASTNOISE":
            return "execute_FastNoise"
        else:
            if self.blenderNoiseType == "NOISE":
                if self.noiseMode == "NOISE":
                    return "execute_Noise"
                elif self.noiseMode == "TURBULENCE":
                    return "execute_Turbulence"
                elif self.noiseMode == "FRACTAL":
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
                if self.noiseVectorMode == "NOISE":
                    return "execute_NoiseVector"
                elif self.noiseVectorMode == "TURBULENCE":
                    return "execute_TurbulenceVector"

            elif self.blenderNoiseType == "VARIABLELACUNARITY":
                return "execute_VariableLacunarity"

    def execute_FastNoise(self, vectors, *settings):
        noise = self.calculateNoise(vectors, *settings)
        return DoubleList.fromValues(noise)

    def execute_Noise(self, vectors, seed, amplitude, frequency, axisScale, offset):
        return blNoise(self.noiseBasis, vectors, seed, amplitude, frequency, axisScale, offset, self.normalization)

    def execute_Turbulence(self, vectors, seed, amplitude, frequency, axisScale, offset, octaves, hard, noiseAmplitude, noiseFrequency):
        return blTurbulence(self.noiseBasis, vectors, seed, amplitude, frequency, axisScale, offset, octaves, hard, noiseAmplitude,
                            noiseFrequency, self.normalization)

    # Fractal Noise Methods:
    def execute_Fractal(self, vectors, seed, amplitude, frequency, axisScale, offset, octaves, hFactor,
                        lacunarity):
        return blFractal(self.noiseBasis, vectors, seed, amplitude, frequency, axisScale, offset, hFactor,
                         lacunarity, octaves, self.normalization)

    def execute_MultiFractal(self, vectors, seed, amplitude, frequency, axisScale, offset, octaves, hFactor,
                             lacunarity):
        return blMultiFractal(self.noiseBasis, vectors, seed, amplitude, frequency, axisScale, offset, hFactor,
                              lacunarity, octaves, self.normalization)

    def execute_HeteroTerrain(self, vectors, seed, amplitude, frequency, axisScale, offset, octaves, hFactor,
                              lacunarity, noiseOffset):
        return blHeteroTerrain(self.noiseBasis, vectors, seed, amplitude, frequency, axisScale, offset, hFactor,
                               lacunarity, octaves, noiseOffset, self.normalization)

    def execute_RigidMultiFractal(self, vectors, seed, amplitude, frequency, axisScale, offset, octaves, hFactor,
                                  lacunarity, noiseOffset, noiseGain):
        return blRigidMultiFractal(self.noiseBasis, vectors, seed, amplitude, frequency, axisScale, offset, hFactor,
                                   lacunarity, octaves, noiseOffset, noiseGain, self.normalization)

    def execute_HybridMultiFractal(self, vectors, seed, amplitude, frequency, axisScale, offset, octaves, hFactor,
                                   lacunarity, noiseOffset, noiseGain):
        return blHybridMultiFractal(self.noiseBasis, vectors, seed, amplitude, frequency, axisScale, offset, hFactor,
                                    lacunarity, octaves, noiseOffset, noiseGain, self.normalization)

    # 3D Noise Methods:
    def execute_NoiseVector(self, vectors, seed, amplitude, frequency, axisScale, offset):
        return blNoiseVector(self.noiseBasis, vectors, seed, amplitude, frequency, axisScale, offset, self.normalization)

    def execute_TurbulenceVector(self, vectors, seed, amplitude, frequency, axisScale, offset, octaves, hard, noiseAmplitude, noiseFrequency):
        return blTurbulenceVector(self.noiseBasis, vectors, seed, amplitude, frequency, axisScale, offset, octaves, hard, noiseAmplitude,
                            noiseFrequency, self.normalization)

    # Variable Lacunarity Methods:
    def execute_VariableLacunarity(self, vectors, seed, amplitude, frequency, axisScale, offset, distortion):
        return blVariableLacunarity(self.noiseBasis, self.noiseBasis2, vectors, seed, amplitude, frequency, axisScale, offset,
                                    distortion, self.normalization)
