import bpy
from bpy.props import *
from ... events import propertyChanged
from ... data_structures import GPLayer, VirtualPyList, VirtualDoubleList, VirtualLongList
from ... base_types import AnimationNode, VectorizedSocket

class SetGPLayerAttributesNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_SetGPLayerAttributesNode"
    bl_label = "Set GP Layer Attributes"
    errorHandlingType = "EXCEPTION"

    useLayerList: VectorizedSocket.newProperty()

    def create(self):
        self.newInput(VectorizedSocket("GPLayer", "useLayerList",
            ("Layer", "layer"), ("Layers", "layers")), dataIsModified = True)
        self.newInput(VectorizedSocket("Text", "useLayerList",
            ("Name", "layerName"), ("Names", "layerNames")), value = 'AN-Layer')
        self.newInput(VectorizedSocket("Text", "useLayerList",
            ("Blend Mode", "blendMode"), ("Blend Modes", "blendModes")), value = 'REGULAR', hide = True)
        self.newInput(VectorizedSocket("Float", "useLayerList",
            ("Opacity", "opacity"), ("Opacities", "opacities")), value = 1, hide = True)
        self.newInput(VectorizedSocket("Integer", "useLayerList",
            ("Pass Index", "passIndex"), ("Pass Indices", "passIndices")), value = 0, hide = True)
        self.newOutput(VectorizedSocket("GPLayer", "useLayerList",
            ("Layer", "layer"), ("Layers", "layers")))

        for socket in self.inputs[1:]:
            socket.useIsUsedProperty = True
            socket.isUsed = False

    def getExecutionCode(self, required):
        s = self.inputs
        if self.useLayerList:
            yield "layerNames = VirtualPyList.create(layerNames, 'AN-Layer')"
            yield "blendModes = VirtualPyList.create(blendModes, 'REGULAR')"
            yield "opacities = VirtualDoubleList.create(opacities, 1)"
            yield "passIndices = VirtualLongList.create(passIndices, 0)"
            yield "for i, layer in enumerate(layers):"
            if s["Names"].isUsed:         yield "    layer.layerName = layerNames[i]"
            if s["Blend Modes"].isUsed:   yield "    self.setBlendMode(layer, blendModes[i])"
            if s["Opacities"].isUsed:     yield "    layer.opacity = opacities[i]"
            if s["Pass Indices"].isUsed:  yield "    layer.passIndex = passIndices[i]"
            yield "    pass"
        else:
            if s["Name"].isUsed:        yield "layer.layerName = layerName"
            if s["Blend Mode"].isUsed:  yield "self.setBlendMode(layer, blendMode)"
            if s["Opacity"].isUsed:     yield "layer.opacity = opacity"
            if s["Pass Index"].isUsed:  yield "layer.passIndex = passIndex"

    def setBlendMode(self, layer, blendMode):
        if blendMode not in ['REGULAR', 'OVERLAY', 'ADD', 'SUBTRACT', 'MULTIPLY', 'DIVIDE']:
            self.raiseErrorMessage("The blend mode is invalid. \n\nPossible values for 'Blend Mode' are: 'REGULAR', 'OVERLAY', 'ADD', 'SUBTRACT', 'MULTIPLY', 'DIVIDE'")
        layer.blendMode = blendMode
        return layer
