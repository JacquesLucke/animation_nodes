import bpy
from ... data_structures import VirtualDoubleList
from ... base_types import AnimationNode, VectorizedSocket

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
            ("Layer", "layer"), ("Layers", "layers")))

    def getExecutionFunctionName(self):
        if self.useLayerList and self.useOpacityList:
            return "execute_LayerList_OpacityList"
        elif self.useOpacityList:
            return "execute_Layer_OpacityList"
        else:
            return "execute_Layer"

    def execute_Layer(self, layer, opacity):
        layer.opacity = opacity
        return layer

    def execute_Layer_OpacityList(self, layer, opacities):
        if len(opacities) == 0: return [layer]

        layers = []
        for opacity in opacities:
            layerNew = layer.copy()
            layerNew.opacity = opacity
            layers.append(layerNew)
        return layers

    def execute_LayerList_OpacityList(self, layers, opacities):
        opacities = VirtualDoubleList.create(opacities, 1)
        for i, layer in enumerate(layers):
            layer.opacity = opacities[i]
        return layers
