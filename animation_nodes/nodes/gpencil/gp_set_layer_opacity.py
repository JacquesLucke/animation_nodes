import bpy
from ... base_types import AnimationNode, VectorizedSocket
from ... data_structures import VirtualDoubleList, VirtualPyList, GPLayer

class GPSetLayerOpacityNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_GPSetLayerOpacityNode"
    bl_label = "GP Set Layer Opacity"

    useLayerList: VectorizedSocket.newProperty()
    useOpacityList: VectorizedSocket.newProperty()

    def create(self):
        self.newInput(VectorizedSocket("GPLayer", "useLayerList",
            ("Layer", "layer"), ("Layers", "layers")), dataIsModified = True)
        self.newInput(VectorizedSocket("Float", "useOpacityList",
            ("Opacity", "opacity"), ("Opacities", "opacities")), value = 1)
        self.newOutput(VectorizedSocket("GPLayer", ["useLayerList", "useOpacityList"],
            ("Layer", "outLayer"), ("Layers", "outLayers")))

    def getExecutionFunctionName(self):
        if self.useLayerList or self.useOpacityList:
            return "execute_LayerList_OpacityList"
        else:
            return "execute_Layer"

    def execute_Layer(self, layer, opacity):
        layer.opacity = opacity
        return layer

    def execute_LayerList_OpacityList(self, layers, opacities):
        _layers = VirtualPyList.create(layers, GPLayer())
        _opacities = VirtualDoubleList.create(opacities, 1)
        amount = VirtualPyList.getMaxRealLength(_layers, _opacities)

        outLayers = []
        for i in range(amount):
            layerNew =_layers[i].copy()
            layerNew.opacity = _opacities[i]
            outLayers.append(layerNew)
        return outLayers
