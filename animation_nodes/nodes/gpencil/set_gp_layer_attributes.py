import bpy
from bpy.props import *
from ... events import propertyChanged
from ... base_types import AnimationNode, VectorizedSocket

class SetGPLayerAttributesNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_SetGPLayerAttributesNode"
    bl_label = "Set GP Layer Attributes"
    errorHandlingType = "EXCEPTION"

    useLayerList: VectorizedSocket.newProperty()
    useNameList: VectorizedSocket.newProperty()
    useBlendModeList: VectorizedSocket.newProperty()
    useOpacityList: VectorizedSocket.newProperty()
    usePassIndexList: VectorizedSocket.newProperty()
    useMaskLayerList: VectorizedSocket.newProperty()

    def create(self):
        self.newInput(VectorizedSocket("GPLayer", "useLayerList",
            ("Layer", "layers"), ("Layers", "layers")), dataIsModified = True)
        self.newInput(VectorizedSocket("Text", "useNameList",
            ("Name", "layerNames"), ("Names", "layerNames")), value = 'AN-Layer', hide = True)
        self.newInput(VectorizedSocket("Text", "useBlendModeList",
            ("Blend Mode", "blendModes"), ("Blend Modes", "blendModes")), value = 'REGULAR', hide = True)
        self.newInput(VectorizedSocket("Float", "useOpacityList",
            ("Opacity", "opacities"), ("Opacities", "opacities")), value = 1, minValue = 0, maxValue = 1)
        self.newInput(VectorizedSocket("Integer", "usePassIndexList",
            ("Pass Index", "passIndices"), ("Pass Indices", "passIndices")), value = 0, minValue = 0)
        self.newInput(VectorizedSocket("Boolean", "useMaskLayerList",
            ("Mask Layer", "masksLayer"), ("Masks Layer", "masksLayer")), value = False)

        self.newOutput(VectorizedSocket("GPLayer",
            ["useLayerList", "useNameList", "useBlendModeList", "useOpacityList", "usePassIndexList", "useMaskLayerList"],
            ("Layer", "outLayer"), ("Layers", "outLayers")))

        for socket in self.inputs[1:]:
            socket.useIsUsedProperty = True
            socket.isUsed = False

    def getExecutionCode(self, required):
        s = self.inputs
        isName = s[1].isUsed
        isBlendMode = s[2].isUsed
        isOpacity = s[3].isUsed
        isPassIndex = s[4].isUsed
        isMaskLayer = s[5].isUsed
        if any([self.useLayerList, self.useNameList, self.useBlendModeList, self.useOpacityList, self.usePassIndexList, self.useMaskLayerList]):
            if any([isName, isBlendMode, isOpacity, isPassIndex, isMaskLayer]):
                if isName:      yield "_layerNames = VirtualPyList.create(layerNames, 'AN-Layer')"
                if isBlendMode: yield "_blendModes = VirtualPyList.create(blendModes, 'REGULAR')"
                if isOpacity:   yield "_opacities = VirtualDoubleList.create(opacities, 1)"
                if isPassIndex: yield "_passIndices = VirtualLongList.create(passIndices, 0)"
                if isMaskLayer: yield "_masksLayer = VirtualBooleanList.create(masksLayer, False)"
                    
                yield                 "_layers = VirtualPyList.create(layers, GPLayer())"
                yield                 "amount = VirtualPyList.getMaxRealLength(_layers"
                if isName:      yield "         , _layerNames"
                if isBlendMode: yield "         , _blendModes"
                if isOpacity:   yield "         , _opacities"
                if isPassIndex: yield "         , _passIndices"
                if isMaskLayer: yield "         , _masksLayer"
                yield                 "         )"

                yield                 "outLayers = []"
                yield                 "for i in range(amount):"
                yield                 "    layerNew = _layers[i].copy()"
                if isName:      yield "    layerNew.layerName = _layerNames[i]"
                if isBlendMode: yield "    self.setBlendMode(layerNew, _blendModes[i])"
                if isOpacity:   yield "    layerNew.opacity = _opacities[i]"
                if isPassIndex: yield "    layerNew.passIndex = _passIndices[i]"
                if isMaskLayer: yield "    layerNew.maskLayer = _masksLayer[i]"
                yield                 "    outLayers.append(layerNew)"
            else:
                yield                 "outLayers = layers"
        else:
            yield                 "outLayer = layers"
            if isName:      yield "outLayer.layerName = layerNames"
            if isBlendMode: yield "self.setBlendMode(outLayer, blendModes)"
            if isOpacity:   yield "outLayer.opacity = opacities"
            if isPassIndex: yield "outLayer.passIndex = passIndices"
            if isMaskLayer: yield "outLayer.maskLayer = masksLayer"

    def setBlendMode(self, layer, blendMode):
        if blendMode not in ['REGULAR', 'OVERLAY', 'ADD', 'SUBTRACT', 'MULTIPLY', 'DIVIDE']:
            self.raiseErrorMessage("The blend mode is invalid. \n\nPossible values for 'Blend Mode' are: 'REGULAR', 'OVERLAY', 'ADD', 'SUBTRACT', 'MULTIPLY', 'DIVIDE'")
        layer.blendMode = blendMode
        return layer
