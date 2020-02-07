import bpy
from bpy.props import *
from mathutils import Matrix
from ... base_types import AnimationNode, VectorizedSocket
from ... data_structures import GPLayer, VirtualPyList, VirtualMatrix4x4List, VirtualVector3DList

transformationTypeItems = [
    ("MATRIX", "Matrix", "", "NONE", 0),
    ("VECTOR", "Vector", "", "NONE", 1)
]

class GPTransformLayerNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_GPTransformLayerNode"
    bl_label = "GP Transform Layer"

    transformationType: EnumProperty(name = "Transformation Type", default = "MATRIX",
        items = transformationTypeItems, update = AnimationNode.refresh)

    useLayerList: VectorizedSocket.newProperty()
    useTransformationList: VectorizedSocket.newProperty()

    def create(self):
        self.newInput(VectorizedSocket("GPLayer", "useLayerList",
            ("Layer", "layer", dict(defaultDrawType = "PROPERTY_ONLY")),
            ("Layers", "layers")), dataIsModified = True)
        if self.transformationType == "VECTOR":
            self.newInput(VectorizedSocket("Vector", "useTransformationList",
                ("Translation", "translation"), ("Translations", "translations")))
        elif self.transformationType == "MATRIX":
            self.newInput(VectorizedSocket("Matrix", "useTransformationList",
                ("Transformation", "transformation"), ("Transformations", "transformations")))

        self.newOutput(VectorizedSocket("GPLayer", ["useLayerList", "useTransformationList"],
                ("Layer", "outLayer"), ("Layers", "outLayers")))

    def draw(self, layout):
        layout.prop(self, "transformationType", text = "")

    def getExecutionFunctionName(self):
        if self.transformationType == "MATRIX":
            if self.useLayerList:
                if self.useTransformationList:
                    return "execute_MultipleLayers_MultipleMatrices"
                else:
                    return "execute_MultipleLayers_SingleMatrix"
            else:
                if self.useTransformationList:
                    return "execute_SingleLayer_MultipleMatrices"
                else:
                    return "execute_Single_Matrix"

        else:
            if self.useLayerList:
                if self.useTransformationList:
                    return "execute_MultipleLayers_MultipleVectors"
                else:
                    return "execute_MultipleLayers_SingleVector"
            else:
                if self.useTransformationList:
                    return "execute_SingleLayer_MultipleVectors"
                else:
                    return "execute_Single_Vector"

    def execute_Single_Matrix(self, layer, matrix):
        self.transfromLayerByMatrix(layer, matrix)
        return layer

    def execute_SingleLayer_MultipleMatrices(self, layer, matrices):
        outLayers = []
        for matrix in matrices:
            layerNew = layer.copy()
            self.transfromLayerByMatrix(layerNew, matrix)
            outLayers.append(layerNew)
        return outLayers

    def execute_MultipleLayers_SingleMatrix(self, layers, matrix):
        for layer in layers:
            self.transfromLayerByMatrix(layer, matrix)
        return layers

    def execute_MultipleLayers_MultipleMatrices(self, layers, matrices):
        _layers = VirtualPyList.create(layers, GPLayer())
        _matrices = VirtualMatrix4x4List.create(matrices, Matrix())
        amount = VirtualPyList.getMaxRealLength(_layers, _matrices)

        outLayers = []
        for i in range(amount):
            layerNew = _layers[i].copy()
            self.transfromLayerByMatrix(layerNew, _matrices[i])
            outLayers.append(layerNew)
        return outLayers

    def execute_Single_Vector(self, layer, vector):
        self.transfromLayerByVector(layer, vector)
        return layer

    def execute_SingleLayer_MultipleVectors(self, layer, vectors):
        outLayers = []
        for vector in vectors:
            layerNew = layer.copy()
            self.transfromLayerByVector(layerNew, vector)
            outLayers.append(layerNew)
        return outLayers

    def execute_MultipleLayers_SingleVector(self, layers, vector):
        for layer in layers:
            self.transfromLayerByVector(layer, vector)
        return layers

    def execute_MultipleLayers_MultipleVectors(self, layers, vectors):
        _layers = VirtualPyList.create(layers, GPLayer())
        _vectors = VirtualVector3DList.create(vectors, (0, 0, 0))
        amount = VirtualPyList.getMaxRealLength(_layers, _vectors)

        outLayers = []
        for i in range(amount):
            layerNew = _layers[i].copy()
            self.transfromLayerByVector(layerNew, _vectors[i])
            outLayers.append(layerNew)
        return outLayers

    def transfromLayerByMatrix(self, layer, matrix):
        for frame in layer.frames:
            for stroke in frame.strokes:
                stroke.vertices.transform(matrix)

    def transfromLayerByVector(self, layer, vector):
        for frame in layer.frames:
            for stroke in frame.strokes:
                stroke.vertices.transform(Matrix.Translation(vector))
