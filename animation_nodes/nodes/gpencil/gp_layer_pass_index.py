import bpy
from ... data_structures import VirtualLongList
from ... base_types import AnimationNode, VectorizedSocket

class GPLayerPassIndexNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_GPLayerPassIndexNode"
    bl_label = "GP Layer Pass Index"

    useLayerList: VectorizedSocket.newProperty()

    def create(self):
        self.newInput(VectorizedSocket("GPLayer", "useLayerList",
            ("Layer", "layer"), ("Layers", "layers")), dataIsModified = True)
        self.newInput(VectorizedSocket("Integer", "useLayerList",
            ("Pass Index", "passIndex"), ("Pass Indices", "passIndices")), value = 0)
        self.newOutput(VectorizedSocket("GPLayer", "useLayerList",
            ("Layer", "layer"), ("Layers", "layers")))

    def getExecutionFunctionName(self):
        if self.useLayerList:
            return "execute_LayerList"
        else:
            return "execute_Layer"

    def execute_Layer(self, layer, passIndex):
        layer.passIndex = passIndex
        return layer

    def execute_LayerList(self, layers, passIndices):
        passIndices = VirtualLongList.create(passIndices, 0)
        for i, layer in enumerate(layers):
            layer.passIndex = passIndices[i]
        return layers
