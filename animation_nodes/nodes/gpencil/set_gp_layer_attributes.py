import bpy
from bpy.props import *
from ... events import propertyChanged
from ... data_structures import GPLayer, VirtualBooleanList
from ... base_types import AnimationNode, VectorizedSocket

class SetGPLayerAttributesNode(AnimationNode, bpy.types.Node):
    bl_idname = "an_SetGPLayerAttributesNode"
    bl_label = "Set GP Layer Attributes"
    errorHandlingType = "EXCEPTION"

    useLayerList: VectorizedSocket.newProperty()
    useNameList: VectorizedSocket.newProperty()
    useBlendModeList: VectorizedSocket.newProperty()
    useOpacityList: VectorizedSocket.newProperty()
    useLightsList: VectorizedSocket.newProperty()
    useTintColorList: VectorizedSocket.newProperty()
    useTintFactorList: VectorizedSocket.newProperty()
    useLineChangeList: VectorizedSocket.newProperty()
    usePassIndexList: VectorizedSocket.newProperty()

    useMaskLayerList: VectorizedSocket.newProperty()
    useInvertMaskLayerList: VectorizedSocket.newProperty()

    def create(self):
        self.newInput(VectorizedSocket("GPLayer", "useLayerList",
            ("Layer", "layers"), ("Layers", "layers")), dataIsModified = True)
        self.newInput(VectorizedSocket("Text", "useNameList",
            ("Name", "layerNames"), ("Names", "layerNames")), value = 'AN-Layer', hide = True)
        self.newInput(VectorizedSocket("Text", "useBlendModeList",
            ("Blend Mode", "blendModes"), ("Blend Modes", "blendModes")), value = 'REGULAR', hide = True)
        self.newInput(VectorizedSocket("Float", "useOpacityList",
            ("Opacity", "opacities"), ("Opacities", "opacities")), value = 1, minValue = 0, maxValue = 1)
        self.newInput(VectorizedSocket("Boolean", "useLightsList",
            ("Use Lights", "useLights"), ("Use Lights", "useLights")), value = False, hide = True)
        self.newInput(VectorizedSocket("Color", "useTintColorList",
            ("Tint Color", "tintColors"), ("Tint Colors", "tintColors")), hide = True)
        self.newInput(VectorizedSocket("Float", "useTintFactorList",
            ("Tint Factor", "tintFactors"), ("Tint Factors", "tintFactors")), value = 0, minValue = 0, maxValue = 1, hide = True)
        self.newInput(VectorizedSocket("Integer", "useLineChangeList",
            ("Stroke Thickness", "lineChanges"), ("Stroke Thicknesses", "lineChanges")), hide = True)
        self.newInput(VectorizedSocket("Integer", "usePassIndexList",
            ("Pass Index", "passIndices"), ("Pass Indices", "passIndices")), value = 0, minValue = 0)
        self.newInput(VectorizedSocket("GPLayer", "useMaskLayerList",
            ("Mask Layer", "maskLayers"), ("Mask Layers", "maskLayers")))
        self.newInput(VectorizedSocket("Boolean", "useInvertMaskLayerList",
            ("Invert Mask Layer", "invertMaskLayers"), ("Invert Mask Layers", "invertMaskLayers")),
            value = False, hide = True)

        self.newOutput(VectorizedSocket("GPLayer",
            ["useLayerList", "useNameList", "useBlendModeList", "useOpacityList", "useLightsList",
            "useTintColorList", "useTintFactorList", "useLineChangeList", "usePassIndexList"],
            ("Layer", "outLayer"), ("Layers", "outLayers")))

        for socket in self.inputs[1:]:
            socket.useIsUsedProperty = True
            socket.isUsed = False

    def getExecutionCode(self, required):
        s = self.inputs
        isName = s[1].isUsed
        isBlendMode = s[2].isUsed
        isOpacity = s[3].isUsed
        isUseLights = s[4].isUsed
        isTintColor = s[5].isUsed
        isTintFactor = s[6].isUsed
        isLineChange = s[7].isUsed
        isPassIndex = s[8].isUsed
        isMaskLayer = s[9].isUsed
        isInvertMaskLayer = s[10].isUsed
        if any([self.useLayerList, self.useNameList, self.useBlendModeList, self.useOpacityList, self.useLightsList,
                self.useTintColorList, self.useTintFactorList, self.useLineChangeList, self.usePassIndexList]):
            if any([isName, isBlendMode, isOpacity, isUseLights, isTintColor, isTintFactor, isLineChange, isPassIndex,
                    isMaskLayer, isInvertMaskLayer]):
                if isName:            yield "_layerNames = VirtualPyList.create(layerNames, 'AN-Layer')"
                if isBlendMode:       yield "_blendModes = VirtualPyList.create(blendModes, 'REGULAR')"
                if isOpacity:         yield "_opacities = VirtualDoubleList.create(opacities, 1)"
                if isUseLights:       yield "_useLights = VirtualBooleanList.create(useLights, False)"
                if isTintColor:       yield "_tintColors = VirtualColorList.create(tintColors, Color((0, 0, 0, 0)))"
                if isTintFactor:      yield "_tintFactors = VirtualDoubleList.create(tintFactors, 0)"
                if isLineChange:      yield "_lineChanges = VirtualLongList.create(lineChanges, 0)"
                if isPassIndex:       yield "_passIndices = VirtualLongList.create(passIndices, 0)"

                yield                       "_layers = VirtualPyList.create(layers, GPLayer())"
                yield                       "amount = VirtualPyList.getMaxRealLength(_layers"
                if isName:            yield "         , _layerNames"
                if isBlendMode:       yield "         , _blendModes"
                if isOpacity:         yield "         , _opacities"
                if isUseLights:       yield "         , _useLights"
                if isTintColor:       yield "         , _tintColors"
                if isTintFactor:      yield "         , _tintFactors"
                if isLineChange:      yield "         , _lineChanges"
                if isPassIndex:       yield "         , _passIndices"
                yield                       "         )"

                yield                       "outLayers = []"
                yield                       "for i in range(amount):"
                yield                       "    layerNew = _layers[i].copy()"
                if isName:            yield "    layerNew.layerName = _layerNames[i]"
                if isBlendMode:       yield "    self.setBlendMode(layerNew, _blendModes[i])"
                if isOpacity:         yield "    layerNew.opacity = _opacities[i]"
                if isUseLights:       yield "    layerNew.useLights = _useLights[i]"
                if isTintColor:       yield "    layerNew.tintColor = _tintColors[i]"
                if isTintFactor:      yield "    layerNew.tintFactor = _tintFactors[i]"
                if isLineChange:      yield "    layerNew.lineChange = _lineChanges[i]"
                if isPassIndex:       yield "    layerNew.passIndex = _passIndices[i]"
                if isMaskLayer:       yield "    self.setMaskLayers(layerNew, maskLayers)"
                if isInvertMaskLayer: yield "    self.setInvertMaskLayers(layerNew, invertMaskLayers)"
                yield                       "    outLayers.append(layerNew)"
            else:
                yield                       "outLayers = layers"
        else:
            yield                       "outLayer = layers"
            if isName:            yield "outLayer.layerName = layerNames"
            if isBlendMode:       yield "self.setBlendMode(outLayer, blendModes)"
            if isOpacity:         yield "outLayer.opacity = opacities"
            if isUseLights:       yield "outLayer.useLights = useLights"
            if isTintColor:       yield "outLayer.tintColor = tintColors"
            if isTintFactor:      yield "outLayer.tintFactor = tintFactors"
            if isLineChange:      yield "outLayer.lineChange = lineChanges"
            if isPassIndex:       yield "outLayer.passIndex = passIndices"
            if isMaskLayer:       yield "self.setMaskLayers(outLayer, maskLayers)"
            if isInvertMaskLayer: yield "self.setInvertMaskLayers(outLayer, invertMaskLayers)"

    def setBlendMode(self, layer, blendMode):
        if blendMode not in ['REGULAR', 'OVERLAY', 'ADD', 'SUBTRACT', 'MULTIPLY', 'DIVIDE']:
            self.raiseErrorMessage("The blend mode is invalid. \n\nPossible values for 'Blend Mode' are: 'REGULAR', 'OVERLAY', 'ADD', 'SUBTRACT', 'MULTIPLY', 'DIVIDE'")
        layer.blendMode = blendMode
        return layer

    def setMaskLayers(self, layer, maskLayersIn):
        if not self.useMaskLayerList:
            maskLayersIn = [maskLayersIn]

        maskLayers = []
        for maskLayer in maskLayersIn:
            if maskLayer.isEmptyLayer(): continue
            maskLayerName = maskLayer.layerName
            if maskLayerName != "" and maskLayer != layer.layerName:
                maskLayers.append(maskLayer)

        layer.maskLayers = maskLayers
        return layer

    def setInvertMaskLayers(self, layer, invertMaskLayers):
        invertMaskLayers = VirtualBooleanList.create(invertMaskLayers, False)

        maskLayers = layer.maskLayers
        for i, maskLayer in enumerate(maskLayers):
            maskLayer.invertAsMask = invertMaskLayers[i]

        layer.maskLayers = maskLayers
        return layer
