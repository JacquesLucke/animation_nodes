import bpy
from ... math import Matrix
from ... base_types import AnimationNode, VectorizedSocket
from ... data_structures import VirtualMatrix4x4List, VirtualPyList, GPLayer

class TransformGPLayerNode(AnimationNode, bpy.types.Node):
    bl_idname = "an_TransformGPLayerNode"
    bl_label = "Transform GP Layer"

    useLayerList: VectorizedSocket.newProperty()
    useMatrixList: VectorizedSocket.newProperty()

    def create(self):
        self.newInput(VectorizedSocket("GPLayer", "useLayerList",
            ("Layer", "layer", dict(defaultDrawType = "PROPERTY_ONLY")),
            ("Layers", "layers")), dataIsModified = True)
        self.newInput(VectorizedSocket("Matrix", "useMatrixList",
            ("Matrix", "matrix"), ("Matices", "matrices")))
        self.newOutput(VectorizedSocket("GPLayer", ["useLayerList", "useMatrixList"],
                ("Layer", "outLayer"), ("Layers", "outLayers")))

    def getExecutionFunctionName(self):
        if self.useLayerList or self.useMatrixList:
            return "execute_LayerList_MatrixList"
        else:
            return "execute_Layer_Matrix"

    def execute_Layer_Matrix(self, layer, matrix):
        if matrix is not None:
            self.transformLayer(layer, matrix)
        return layer

    def execute_LayerList_MatrixList(self, layers, matrices):
        _layers = VirtualPyList.create(layers, GPLayer())
        _matrices = VirtualMatrix4x4List.create(matrices, Matrix())
        amount = VirtualPyList.getMaxRealLength(_layers, _matrices)

        outLayers = []
        for i in range(amount):
            layerNew = _layers[i].copy()
            self.transformLayer(layerNew, _matrices[i])
            outLayers.append(layerNew)
        return outLayers

    def transformLayer(self, layer, matrix):
        for frame in layer.frames:
            for stroke in frame.strokes:
                stroke.vertices.transform(matrix)
