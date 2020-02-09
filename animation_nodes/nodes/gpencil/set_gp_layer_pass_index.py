import bpy
from ... base_types import AnimationNode, VectorizedSocket
from ... data_structures import VirtualLongList, VirtualPyList, GPLayer

class SetGPLayerPassIndexNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_SetGPLayerPassIndexNode"
    bl_label = "Set GP Layer Pass Index"

    useLayerList: VectorizedSocket.newProperty()
    usePassIndexList: VectorizedSocket.newProperty()

    def create(self):
        self.newInput(VectorizedSocket("GPLayer", "useLayerList",
            ("Layer", "layer"), ("Layers", "layers")), dataIsModified = True)
        self.newInput(VectorizedSocket("Integer", "usePassIndexList",
            ("Pass Index", "passIndex"), ("Pass Indices", "passIndices")), value = 0)
        self.newOutput(VectorizedSocket("GPLayer", ["useLayerList", "usePassIndexList"],
            ("Layer", "outLayer"), ("Layers", "outLayers")))

    def getExecutionFunctionName(self):
        if self.useLayerList or self.usePassIndexList:
            return "execute_LayerList_PassIndexList"
        else:
            return "execute_Layer_PassIndex"

    def execute_Layer_PassIndex(self, layer, passIndex):
        layer.passIndex = passIndex
        return layer

    def execute_LayerList_PassIndexList(self, layers, passIndices):
        _layers = VirtualPyList.create(layers, GPLayer())
        _passIndices = VirtualLongList.create(passIndices, 0)
        amount = VirtualPyList.getMaxRealLength(_layers, _passIndices)

        outLayers = []
        for i in range(amount):
            layerNew = _layers[i].copy()
            layerNew.passIndex = _passIndices[i]
            outLayers.append(layerNew)
        return outLayers
