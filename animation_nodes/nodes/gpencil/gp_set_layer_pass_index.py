import bpy
from ... data_structures import VirtualLongList
from ... base_types import AnimationNode, VectorizedSocket

class GPSetLayerPassIndexNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_GPSetLayerPassIndexNode"
    bl_label = "GP Set Layer Pass Index"

    useLayerList: VectorizedSocket.newProperty()
    usePassIndexList: VectorizedSocket.newProperty()

    def create(self):
        self.newInput(VectorizedSocket("GPLayer", "useLayerList",
            ("Layer", "layer"), ("Layers", "layers")), dataIsModified = True)
        self.newInput(VectorizedSocket("Integer", "usePassIndexList",
            ("Pass Index", "passIndex"), ("Pass Indices", "passIndices")), value = 0)
        self.newOutput(VectorizedSocket("GPLayer", ["useLayerList", "usePassIndexList"],
            ("Layer", "layer"), ("Layers", "layers")))

    def getExecutionFunctionName(self):
        if self.useLayerList:
            return "execute_LayerList_PassIndexList"
        elif self.usePassIndexList:
            return "execute_Layer_PassIndexList"
        else:
            return "execute_Layer_PassIndex"

    def execute_Layer_PassIndex(self, layer, passIndex):
        layer.passIndex = passIndex
        return layer

    def execute_Layer_PassIndexList(self, layer, passIndices):
        if len(passIndices) == 0: return [layer]

        layers = []
        for passIndex in passIndices:
            layerNew = layer.copy()
            layerNew.passIndex = passIndex
            layers.append(layerNew)
        return layers

    def execute_LayerList_PassIndexList(self, layers, passIndices):
        passIndices = VirtualLongList.create(passIndices, 0)
        for i, layer in enumerate(layers):
            layer.passIndex = passIndices[i]
        return layers
