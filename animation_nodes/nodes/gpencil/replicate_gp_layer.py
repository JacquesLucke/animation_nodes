import bpy
from bpy.props import *
from mathutils import Matrix
from ... data_structures import GPLayer, VirtualDoubleList
from ... base_types import AnimationNode, VectorizedSocket

transformationTypeItems = [
    ("Matrix List", "Matrices", "", "NONE", 0),
    ("Vector List", "Vectors", "", "NONE", 1)
]

class ReplicateGPLayerNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_ReplicateGPLayerNode"
    bl_label = "Replicate GP Layer"

    useLayerList: VectorizedSocket.newProperty()

    transformationType: EnumProperty(name = "Transformation Type", default = "Matrix List",
        items = transformationTypeItems, update = AnimationNode.refresh)

    def create(self):
        self.newInput(VectorizedSocket("GPLayer", "useLayerList",
            ("Layer", "layer", dict(defaultDrawType = "PROPERTY_ONLY")),
            ("Layers", "layers")))
        self.newInput(self.transformationType, "Transformations", "transformations")
        self.newInput("Float List", "Offset Frame Numbers", "offsets", value = 0, hide = True)

        self.newOutput("GPLayer List", "Layers", "outLayers")

    def draw(self, layout):
        layout.prop(self, "transformationType", text = "")

    def getExecutionFunctionName(self):
        if self.transformationType == "Matrix List":
            return "execute_MatrixList"
        elif self.transformationType == "Vector List":
            return "execute_VectorList"

    def execute_MatrixList(self, layers, matrices, offsets):
        if isinstance(layers, GPLayer):
            layers = [layers]

        _offsets = VirtualDoubleList.create(offsets, 0)

        outLayers = []
        for i, matrix in enumerate(matrices):
            for layer in layers:
                newLayer = layer.copy()
                self.transformLayerByMatrix(newLayer, _offsets[i], matrix)
                outLayers.append(newLayer)
        return outLayers

    def execute_VectorList(self, layers, vectors, offsets):
        if isinstance(layers, GPLayer):
            layers = [layers]

        _offsets = VirtualDoubleList.create(offsets, 0)

        outLayers = []
        for i, vector in enumerate(vectors):
            for layer in layers:
                newLayer = layer.copy()
                self.transformLayerByMatrix(newLayer, _offsets[i], vector)
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
                stroke.vertices.transform(Matrix.Translation(vector))
