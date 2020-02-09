import bpy
from ... data_structures import VirtualPyList, GPLayer
from ... base_types import AnimationNode, VectorizedSocket

class SetGPLayerBlendModeNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_SetGPLayerBlendModeNode"
    bl_label = "Set GP Layer Blend Mode"
    errorHandlingType = "EXCEPTION"

    useLayerList: VectorizedSocket.newProperty()
    useModeTextList: VectorizedSocket.newProperty()

    def create(self):
        self.newInput(VectorizedSocket("GPLayer", "useLayerList",
            ("Layer", "layer"), ("Layers", "layers")), dataIsModified = True)
        self.newInput(VectorizedSocket("Text", "useModeTextList",
            ("Blend Mode", "blendMode"), ("Blend Modes", "blendModes")), value = "REGULAR")
        self.newOutput(VectorizedSocket("GPLayer", ["useLayerList", "useModeTextList"],
            ("Layer", "outLayer"), ("Layers", "outLayers")))

    def getExecutionFunctionName(self):
        if self.useLayerList or self.useModeTextList:
            return "execute_LayerList_BlendModeList"
        else:
            return "execute_Layer_BlendMode"

    def execute_Layer_BlendMode(self, layer, blendMode):
        return self.setLayerBlendMode(layer, blendMode)

    def execute_LayerList_BlendModeList(self, layers, blendModes):
        _layers = VirtualPyList.create(layers, GPLayer())
        _blendModes = VirtualPyList.create(blendModes, "REGULAR")
        amount = VirtualPyList.getMaxRealLength(_layers, _blendModes)

        outLayers = []
        for i in range(amount):
            layerNew =_layers[i].copy()
            self.setLayerBlendMode(layerNew, _blendModes[i])
            outLayers.append(layerNew)
        return outLayers

    def setLayerBlendMode(self, layer, blendMode):
        if blendMode not in ['REGULAR', 'OVERLAY', 'ADD', 'SUBTRACT', 'MULTIPLY', 'DIVIDE']:
            self.raiseErrorMessage("The Blend Mode is invalid. \n\nPossible values for 'Blend Mode' are: 'REGULAR', 'OVERLAY', 'ADD', 'SUBTRACT', 'MULTIPLY', 'DIVIDE'")

        layer.blendMode = blendMode
        return layer
