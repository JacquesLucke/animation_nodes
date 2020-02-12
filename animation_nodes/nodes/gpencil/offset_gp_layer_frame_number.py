import bpy
from ... base_types import AnimationNode, VectorizedSocket
from ... data_structures import VirtualDoubleList, VirtualPyList, GPLayer

class OffsetGPLayerFrameNumberNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_OffsetGPLayerFrameNumberNode"
    bl_label = "Offset GP Layer Frame Number"

    useLayerList: VectorizedSocket.newProperty()
    useFrameNumberList: VectorizedSocket.newProperty()

    def create(self):
        self.newInput(VectorizedSocket("GPLayer", "useLayerList",
            ("Layer", "layer"), ("Layers", "layers")), dataIsModified = True)
        self.newInput(VectorizedSocket("Float", "useFrameNumberList",
            ("Offset Frame Number", "offset"), (" Offset Frame Numbers", "offsets")), value = 0)
        self.newOutput(VectorizedSocket("GPLayer", ["useLayerList", "useFrameNumberList"],
            ("Layer", "outLayer"), ("Layers", "outLayers")))

    def getExecutionFunctionName(self):
        if self.useLayerList or self.useFrameNumberList:
            return "execute_LayerList_FrameNumberList"
        else:
            return "execute_Layer_FrameNumber"

    def execute_Layer_FrameNumber(self, layer, offset):
        layerNew = layer.copy()
        for frame in layerNew.frames:
            frame.frameNumber += offset
        return layerNew

    def execute_LayerList_FrameNumberList(self, layers, offsets):
        _layers = VirtualPyList.create(layers, GPLayer())
        _offsets = VirtualDoubleList.create(offsets, 0)
        amount = VirtualPyList.getMaxRealLength(_layers, _offsets)

        outLayers = []
        for i in range(amount):
            layerNew = _layers[i].copy()
            for frame in layerNew.frames:
                frame.frameNumber += _offsets[i]
            outLayers.append(layerNew)
        return outLayers
