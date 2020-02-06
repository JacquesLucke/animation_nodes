import bpy
from ... base_types import AnimationNode, VectorizedSocket

class GPLayerBlendModeNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_GPLayerBlendModeNode"
    bl_label = "GP Layer Blend Mode"
    errorHandlingType = "EXCEPTION"

    useLayerList: VectorizedSocket.newProperty()
    useModeTextList: VectorizedSocket.newProperty()

    def create(self):
        self.newInput(VectorizedSocket("GPLayer", "useLayerList",
            ("Layer", "layer"), ("Layers", "layers")), dataIsModified = True)
        self.newInput(VectorizedSocket("Text", ["useLayerList", "useModeTextList"],
            ("Blend Mode", "blendMode"), ("Blend Modes", "blendModes")), value = "REGULAR")
        self.newOutput(VectorizedSocket("GPLayer", "useLayerList",
            ("Layer", "layer"), ("Layers", "layers")))

    def getExecutionFunctionName(self):
        if self.useLayerList and self.useModeTextList:
            return "execute_LayerList_BlendModeList"
        elif self.useLayerList:
            return "execute_LayerList_BlendMode"
        else:
            return "execute_Layer_BlendMode"

    def execute_Layer_BlendMode(self, layer, blendMode):
        return self.setLayerBlendMode(layer, blendMode)

    def execute_LayerList_BlendMode(self, layers, blendMode):
        if len(layers) == 0: return layers
        for layer in layers:
            self.setLayerBlendMode(layer, blendMode)
        return layers

    def execute_LayerList_BlendModeList(self, layers, blendModes):
        if len(layers) == 0 or len(blendModes) == 0: return layers
        if len(layers) != len(blendModes):
            self.raiseErrorMessage("Layers and Blend Modes have different lengths.")
        for i, layer in enumerate(layers):
            blendMode = blendModes[i]
            self.setLayerBlendMode(layer, blendMode)
        return layers

    def setLayerBlendMode(self, layer, blendMode):
        if blendMode not in ['REGULAR', 'OVERLAY', 'ADD', 'SUBTRACT', 'MULTIPLY', 'DIVIDE']:
            self.raiseErrorMessage("The Blend Mode is invalid. \n\nPossible values for 'Blend Mode' are: 'REGULAR', 'OVERLAY', 'ADD', 'SUBTRACT', 'MULTIPLY', 'DIVIDE'")

        layer.blendMode = blendMode
        return layer
