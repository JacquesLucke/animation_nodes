import bpy
from bpy.props import *
from ... events import propertyChanged
from ... base_types import AnimationNode, VectorizedSocket
from ... data_structures import GPLayer, VirtualBooleanList

class GPLayerFromFramesNode(AnimationNode, bpy.types.Node):
    bl_idname = "an_GPLayerFromFramesNode"
    bl_label = "GP Layer From Frames"
    errorHandlingType = "EXCEPTION"

    useFrameList: VectorizedSocket.newProperty()
    useMaskLayerList: VectorizedSocket.newProperty()
    useInvertMaskLayerList: VectorizedSocket.newProperty()

    def create(self):
        self.newInput(VectorizedSocket("GPFrame", "useFrameList",
            ("Frame", "frame"), ("Frames", "frames")), dataIsModified = True)
        self.newInput("Text", "Name", "layerName", value = 'AN-Layer')
        self.newInput("Text", "Blend Mode", "blendMode", value = 'REGULAR')
        self.newInput("Float", "Opacity", "opacity", value = 1, minValue = 0, maxValue = 1)
        self.newInput("Boolean", "Use Lights", "useLights", value = True, hide = True)
        self.newInput("Color", "Tint Color", "tintColor", hide = True)
        self.newInput("Float", "Tint Factor", "tintFactor", value = 0, minValue = 0, maxValue = 1, hide = True)
        self.newInput("Integer", "Stroke Thickness", "lineChange", hide = True)
        self.newInput("Integer", "Pass Index", "passIndex", value = 0, minValue = 0, hide = True)
        self.newInput(VectorizedSocket("GPLayer", "useMaskLayerList",
            ("Mask Layer", "maskLayer"), ("Mask Layers", "maskLayers")), hide = True)
        self.newInput(VectorizedSocket("Boolean", "useInvertMaskLayerList",
            ("Invert Mask Layer", "invertMaskLayer"), ("Invert Mask Layers", "invertMaskLayers")),
            value = False, hide = True)

        self.newOutput("GPLayer", "Layer", "layer")

    def execute(self, frames, layerName, blendMode, opacity, useLights, tintColor, tintFactor, lineChange,
                passIndex, maskLayersIn, invertMaskLayers):
        if not self.useFrameList:
            frames = [frames]
        if not self.useMaskLayerList:
            maskLayersIn = [maskLayersIn]

        frameNumbers = [frame.frameNumber for frame in frames]
        if len(frameNumbers) != len(set(frameNumbers)):
            self.raiseErrorMessage("Some Frame Numbers are repeated.")
        if layerName == "":
            self.raiseErrorMessage("Layer name can't be empty.")
        if blendMode not in ['REGULAR', 'OVERLAY', 'ADD', 'SUBTRACT', 'MULTIPLY', 'DIVIDE']:
            self.raiseErrorMessage("The blend mode is invalid. \n\nPossible values for 'Blend Mode' are: 'REGULAR', 'OVERLAY', 'ADD', 'SUBTRACT', 'MULTIPLY', 'DIVIDE'")

        maskLayers = []
        if len(maskLayersIn) > 0:
            invertMaskLayers = VirtualBooleanList.create(invertMaskLayers, False)
            for i, maskLayer in enumerate(maskLayersIn):
                if maskLayer.isEmptyLayer(): continue
                maskLayerName = maskLayer.layerName
                if maskLayerName != "" and maskLayerName != layerName:
                    maskLayer.invertAsMask = invertMaskLayers[i]
                    maskLayers.append(maskLayer)

        return GPLayer(layerName, frames, blendMode, opacity, useLights, tintColor, tintFactor, lineChange,
                       passIndex, False, maskLayers)
