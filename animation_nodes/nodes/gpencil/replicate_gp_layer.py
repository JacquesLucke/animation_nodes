import bpy
from bpy.props import *
from mathutils import Matrix
from ... base_types import AnimationNode, VectorizedSocket
from ... data_structures import GPLayer, Color, VirtualDoubleList, VirtualLongList, VirtualColorList

transformationTypeItems = [
    ("MATRIX_LIST", "Matrices", "", "NONE", 0),
    ("VECTOR_LIST", "Vectors", "", "NONE", 1)
]

class ReplicateGPLayerNode(AnimationNode, bpy.types.Node):
    bl_idname = "an_ReplicateGPLayerNode"
    bl_label = "Replicate GP Layer"

    transformationType: EnumProperty(name = "Transformation Type", default = "MATRIX_LIST",
        items = transformationTypeItems, update = AnimationNode.refresh)

    useLayerList: VectorizedSocket.newProperty()
    useOffsetList: VectorizedSocket.newProperty()
    useTintColorList: VectorizedSocket.newProperty()
    useTintFactorList: VectorizedSocket.newProperty()
    useLineChangeList: VectorizedSocket.newProperty()

    def create(self):
        self.newInput(VectorizedSocket("GPLayer", "useLayerList",
            ("Layer", "layers"), ("Layers", "layers")), dataIsModified = True)
        if self.transformationType == "MATRIX_LIST":
            self.newInput("Matrix List", "Transformations", "transformations")
        else:
            self.newInput("Vector List", "Transformations", "transformations")
        self.newInput(VectorizedSocket("Integer", "useOffsetList",
            ("Offset Frame", "offsets"), ("Offset Frames", "offsets")), value = 0, hide = True)
        self.newInput(VectorizedSocket("Color", "useTintColorList",
            ("Tint Color", "tintColors"), ("Tint Colors", "tintColors")), hide = True)
        self.newInput(VectorizedSocket("Float", "useTintFactorList",
            ("Tint Factor", "tintFactors"), ("Tint Factors", "tintFactors")), value = 0, hide = True)
        self.newInput(VectorizedSocket("Integer", "useLineChangeList",
            ("Stroke Thickness", "lineChanges"), ("Stroke Thicknesses", "lineChanges")), value = 0, hide = True)

        self.newOutput("GPLayer List", "Layers", "outLayers")

    def draw(self, layout):
        layout.prop(self, "transformationType", text = "")

    def getExecutionFunctionName(self):
        if self.transformationType == "MATRIX_LIST":
            return "execute_MatrixList"
        elif self.transformationType == "VECTOR_LIST":
            return "execute_VectorList"

    def execute_MatrixList(self, layers, matrices, offsets, tintColors, tintFactors, lineChanges):
        if isinstance(layers, GPLayer):
            layers = [layers]

        _offsets = VirtualLongList.create(offsets, 0)
        _tintColors = VirtualColorList.create(tintColors, Color((0, 0, 0, 0)))
        _tintFactors = VirtualDoubleList.create(tintFactors, 0)
        _lineChanges = VirtualLongList.create(lineChanges, 0)

        outLayers = []
        for i, matrix in enumerate(matrices):
            for layer in layers:
                newLayer = layer.copy()
                newLayer.layerName = layer.layerName + "-" + str(i)
                newLayer.tintColor = _tintColors[i]
                newLayer.tintFactor = _tintFactors[i]
                newLayer.lineChange = _lineChanges[i]
                self.transformLayerByMatrix(newLayer, _offsets[i], matrix)
                outLayers.append(newLayer)
        return outLayers

    def execute_VectorList(self, layers, vectors, offsets, tintColors, tintFactors, lineChanges):
        if isinstance(layers, GPLayer):
            layers = [layers]

        _offsets = VirtualLongList.create(offsets, 0)
        _tintColors = VirtualColorList.create(tintColors, Color((0, 0, 0, 0)))
        _tintFactors = VirtualDoubleList.create(tintFactors, 0)
        _lineChanges = VirtualLongList.create(lineChanges, 0)

        outLayers = []
        for i, vector in enumerate(vectors):
            for layer in layers:
                newLayer = layer.copy()
                newLayer.layerName = layer.layerName + "-" + str(i)
                newLayer.tintColor = _tintColors[i]
                newLayer.tintFactor = _tintFactors[i]
                newLayer.lineChange = _lineChanges[i]
                self.transformLayerByVector(newLayer, _offsets[i], vector)
                outLayers.append(newLayer)
        return outLayers

    def transformLayerByMatrix(self, layer, offset, matrix):
        for frame in layer.frames:
            frame.frameNumber += offset
            for stroke in frame.strokes:
                stroke.vertices.transform(matrix)

    def transformLayerByVector(self, layer, offset, vector):
        for frame in layer.frames:
            frame.frameNumber += offset
            for stroke in frame.strokes:
                stroke.vertices.move(vector)
