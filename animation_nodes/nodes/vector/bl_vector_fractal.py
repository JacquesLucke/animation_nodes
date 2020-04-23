import bpy
from mathutils import noise
from bpy.props import *
from ... events import propertyChanged
from ... base_types import AnimationNode, VectorizedSocket
from ... data_structures import Vector3DList, DoubleList

noiseModeItems = [
    ("FRACTAL", "Fractal", "", "", 0),
    ("MULTI_FRACTAL", "Multi Fractal", "", "", 1),
    ("HETERO_TERRAIN", "Hetero Terrain", "", "", 2),
    ("RIDGED_MULTI_FRACTAL", "Ridged Multi Fractal", "", "", 3),
    ("HYBRID_MULTI_FRACTAL", "Hybrid Multi Fractal", "", "", 4)
]

vectorFractalModeItems = [
    ("PERLIN_ORIGINAL", "Perlin Orginal", "", "", 0),
    ("PERLIN_NEW", "Perlin New", "", "", 1),
    ("VORONOI_F1", "Voronoi F1", "", "", 2),
    ("VORONOI_F2", "Voronoi F2", "", "", 3),
    ("VORONOI_F3", "Voronoi F3", "", "", 4),
    ("VORONOI_F4", "Voronoi F4", "", "", 5),
    ("VORONOI_F2F1", "Voronoi F2F1", "", "", 6),
    ("VORONOI_CRACKLE", "Voronoi Crackle", "", "", 7),
    ("CELLNOISE", "Cell Noise", "", "", 8)
]

class BLVectorFractalNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_BLVectorFractal"
    bl_label = "BL Vector Fractal"
    bl_width_default = 160

    __annotations__ = {}

    __annotations__["noisemode"] = EnumProperty(name = "Type ", default = "FRACTAL",
        items = noiseModeItems, update = AnimationNode.refresh)

    __annotations__["noisebasis"] = EnumProperty(name = "Basis ", default = "PERLIN_ORIGINAL",
        items = vectorFractalModeItems, update = AnimationNode.refresh)

    useVectorList: VectorizedSocket.newProperty()    

    def create(self):
        self.newInput(VectorizedSocket("Vector", "useVectorList",
            ("Vector", "v"), ("Vectors", "vectorsIn")))       
        self.newInput("Float", "H", "h")
        self.newInput("Float", "Lacunarity", "lacunarity")
        self.newInput("Integer", "Octaves", "octaves", value = 2, minValue = 1)
        if self.noisemode == "HETERO_TERRAIN":
            self.newInput("Float", "Offset", "offset")
        if self.noisemode == "RIDGED_MULTI_FRACTAL" or self.noisemode == "HYBRID_MULTI_FRACTAL" :
            self.newInput("Float", "Offset", "offset")
            self.newInput("Float", "Gain", "gain")   

        self.newOutput(VectorizedSocket("Float", ["useVectorList"],
            ("Noise", "noise_out"), ("Noise", "noises_out")))
    
    def draw(self, layout):
        layout.prop(self, "noisemode")
        layout.prop(self, "noisebasis")

    def getExecutionFunctionName(self):
        if self.useVectorList:
            if self.noisemode == "FRACTAL":
                return "execute_fractal"
            elif self.noisemode == "MULTI_FRACTAL":
                return "execute_multifractal"
            elif self.noisemode == "HETERO_TERRAIN":
                return "execute_heteroterrain"
            elif self.noisemode == "RIDGED_MULTI_FRACTAL":
                return "execute_rigidmultifractal"
            elif self.noisemode == "HYBRID_MULTI_FRACTAL":
                return "execute_hybridmultifractal"                
        else:
            if self.noisemode == "FRACTAL":
                return "execute_fractal_s"
            elif self.noisemode == "MULTI_FRACTAL":
                return "execute_multifractal_s"
            elif self.noisemode == "HETERO_TERRAIN":
                return "execute_heteroterrain_s"
            elif self.noisemode == "RIDGED_MULTI_FRACTAL":
                return "execute_rigidmultifractal_s"
            elif self.noisemode == "HYBRID_MULTI_FRACTAL":
                return "execute_hybridmultifractal_s"

    def execute_fractal(self, vectorsIn, h, lacunarity ,octaves):
        noisebasis = self.noisebasis
        return DoubleList.fromValues([noise.fractal(v, h, lacunarity, octaves, noise_basis=noisebasis) for v in vectorsIn])
    def execute_multifractal(self, vectorsIn, h, lacunarity ,octaves):
        noisebasis = self.noisebasis
        return DoubleList.fromValues([noise.multi_fractal(v, h, lacunarity, octaves, noise_basis=noisebasis) for v in vectorsIn])
    def execute_heteroterrain(self, vectorsIn, h, lacunarity ,octaves, offset):
        noisebasis = self.noisebasis
        return DoubleList.fromValues([noise.hetero_terrain(v, h, lacunarity, octaves, offset, noise_basis=noisebasis) for v in vectorsIn])
    def execute_rigidmultifractal(self, vectorsIn, h, lacunarity ,octaves, offset, gain):
        noisebasis = self.noisebasis
        return DoubleList.fromValues([noise.ridged_multi_fractal(v, h, lacunarity, octaves, offset, gain, noise_basis=noisebasis) for v in vectorsIn])
    def execute_hybridmultifractal(self, vectorsIn, h, lacunarity ,octaves, offset, gain):           
        noisebasis = self.noisebasis
        return DoubleList.fromValues([noise.hybrid_multi_fractal(v, h, lacunarity, octaves, offset, gain, noise_basis=noisebasis) for v in vectorsIn])


    def execute_fractal_s(self, v, h, lacunarity ,octaves):
        noisebasis = self.noisebasis
        return noise.fractal(v, h, lacunarity, octaves, noise_basis=noisebasis)
    def execute_multifractal_s(self, v, h, lacunarity ,octaves):
        noisebasis = self.noisebasis
        return noise.multi_fractal(v, h, lacunarity, octaves, noise_basis=noisebasis)
    def execute_heteroterrain_s(self, v, h, lacunarity ,octaves, offset):
        noisebasis = self.noisebasis
        return noise.hetero_terrain(v, h, lacunarity, octaves, offset, noise_basis=noisebasis)
    def execute_rigidmultifractal_s(self, v, h, lacunarity ,octaves, offset, gain):
        noisebasis = self.noisebasis
        return noise.ridged_multi_fractal(v, h, lacunarity, octaves, offset, gain, noise_basis=noisebasis)    
    def execute_hybridmultifractal_s(self, v, h, lacunarity ,octaves, offset, gain):           
        noisebasis = self.noisebasis
        return noise.hybrid_multi_fractal(v, h, lacunarity, octaves, offset, gain, noise_basis=noisebasis)    


