import bpy
from ... data_structures import VirtualDoubleList
from ... base_types import AnimationNode, VectorizedSocket

class GPLayerOpacityNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_GPLayerOpacityNode"
    bl_label = "GP Layer Opacity"

    useLayerList: VectorizedSocket.newProperty()

    def create(self):
        self.newInput(VectorizedSocket("GPLayer", "useLayerList",
            ("Layer", "layer"), ("Layers", "layers")), dataIsModified = True)
        self.newInput(VectorizedSocket("Float", "useLayerList",
            ("Opacity", "opacity"), ("Opacities", "opacities")), value = 1)
        self.newOutput(VectorizedSocket("GPLayer", "useLayerList",
            ("Layer", "layer"), ("Layers", "layers")))

    def getExecutionFunctionName(self):
        if self.useLayerList:
            return "execute_LayerList"
        else:
            return "execute_Layer"

    def execute_Layer(self, layer, opacity):
        layer.opacity = opacity
        return layer

    def execute_LayerList(self, layers, opacities):
        opacities = VirtualDoubleList.create(opacities, 1)
        for i, layer in enumerate(layers):
            layer.opacity = opacities[i]
        return layers
