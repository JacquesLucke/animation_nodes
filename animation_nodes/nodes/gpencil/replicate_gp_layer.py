import bpy
from bpy.props import *
from mathutils import Matrix
from ... base_types import AnimationNode, VectorizedSocket
from ... data_structures import GPLayer, Color, VirtualDoubleList, VirtualLongList, VirtualColorList

transformationTypeItems = [
    ("Matrix List", "Matrices", "", "NONE", 0),
    ("Vector List", "Vectors", "", "NONE", 1)
]

class ReplicateGPLayerNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_ReplicateGPLayerNode"
    bl_label = "Replicate GP Layer"

    transformationType: EnumProperty(name = "Transformation Type", default = "Matrix List",
        items = transformationTypeItems, update = AnimationNode.refresh)

    useLayerList: VectorizedSocket.newProperty()
    useOffsetList: VectorizedSocket.newProperty()
    useTintColorList: VectorizedSocket.newProperty()
    useTintFactorList: VectorizedSocket.newProperty()
    useLineChangeList: VectorizedSocket.newProperty()

    def create(self):
        self.newInput(VectorizedSocket("GPLayer", "useLayerList",
            ("Layer", "layers"), ("Layers", "layers")), dataIsModified = True)
        self.newInput(self.transformationType, "Transformations", "transformations")
        self.newInput(VectorizedSocket("Float", "useOffsetList",
            ("Offset Frame", "offsets"), ("Offset Frames", "offsets")), value = 0, hide = True)
        self.newInput(VectorizedSocket("Color", "useTintColorList",
            ("Tint Color", "tintColors"), ("Tint Colors", "tintColors")), hide = True)
        self.newInput(VectorizedSocket("Float", "useTintFactorList",
            ("Tint Factor", "tintFactors"), ("Tint Factors", "tintFactors")), value = 0, hide = True)
        self.newInput(VectorizedSocket("Float", "useLineChangeList",
            ("Stroke Thickness", "lineChanges"), ("Stroke Thicknesses", "lineChanges")), value = 0, hide = True)

        self.newOutput("GPLayer List", "Layers", "outLayers")

    def draw(self, layout):
        layout.prop(self, "transformationType", text = "")

    def getExecutionFunctionName(self):
        if self.transformationType == "Matrix List":
            return "execute_MatrixList"
        elif self.transformationType == "Vector List":
            return "execute_VectorList"

    def execute_MatrixList(self, layers, matrices, offsets, tintColors, tintFactors, lineChanges):
        if isinstance(layers, GPLayer):
            layers = [layers]

        _offsets = VirtualDoubleList.create(offsets, 0)
        _tintColors = VirtualColorList.create(tintColors, Color((0, 0, 0, 0)))
        _tintFactors = VirtualDoubleList.create(tintFactors, 0)
        _lineChanges = VirtualDoubleList.create(lineChanges, 0)

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

        _offsets = VirtualDoubleList.create(offsets, 0)
        _tintColors = VirtualColorList.create(tintColors, Color((0, 0, 0, 0)))
        _tintFactors = VirtualDoubleList.create(tintFactors, 0)
        _lineChanges = VirtualDoubleList.create(lineChanges, 0)

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
