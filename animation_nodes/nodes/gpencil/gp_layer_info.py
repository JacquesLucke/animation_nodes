import bpy
from bpy.props import *
from ... events import propertyChanged
from ... base_types import AnimationNode, VectorizedSocket
from ... data_structures import GPFrame, LongList, BooleanList

frameTypeItems = [
    ("ACTIVE", "Active Frame", "Get active Frame", "NONE", 0),
    ("INDEX", "Frame Index", "Get specific Frame with index", "NONE", 1),
    ("FRAME", "Frame Number", "Get specific Frame with frame-number", "NONE", 2),
    ("ALL", "All Frames", "Get all frames", "NONE", 3)
]

class GPLayerInfoNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_GPLayerInfoNode"
    bl_label = "GP Layer Info"
    errorHandlingType = "EXCEPTION"

    frameType: EnumProperty(name = "Frame Type", default = "ACTIVE",
        items = frameTypeItems, update = AnimationNode.refresh)

    useFrameList: VectorizedSocket.newProperty()

    def create(self):
        self.newInput("GPLayer", "Layer", "layer", dataIsModified = True)

        if self.frameType == "ACTIVE":
            self.newInput("Scene", "Scene", "scene", hide = True)
            self.newOutput("GPFrame", "Frame", "frame")

        elif self.frameType == "INDEX":
            self.newInput(VectorizedSocket("Integer", "useFrameList",
            ("Frame Index", "frameIndex"), ("Frame Indices", "frameIndices")), value = 0)
            self.newOutput(VectorizedSocket("GPFrame", "useFrameList",
            ("Frame", "frame"), ("Frames", "frames")))

        elif self.frameType == "FRAME":
            self.newInput(VectorizedSocket("Float", "useFrameList",
            ("Frame Number", "frameNumber"), ("Frame Numbers", "inFrameNumbers")), value = 1)
            self.newOutput(VectorizedSocket("GPFrame", "useFrameList",
            ("Frame", "frame"), ("Frames", "frames")))

        elif self.frameType == "ALL":
            self.newOutput("GPFrame List", "Frames", "frames")

        self.newOutput("Text", "Name", "layerName", hide = True)
        self.newOutput("Text", "Blend Mode", "blendMode", hide = True)
        self.newOutput("Float", "Opacity", "opacity", hide = True)
        self.newOutput("Color", "Tint Color", "tintColor", hide = True)
        self.newOutput("Float", "Tint Factor", "tintFactor", hide = True)
        self.newOutput("Float", "Stroke Thickness", "lineChange", hide = True)
        self.newOutput("Integer", "Pass Index", "passIndex", hide = True)
        self.newOutput("Text List", "Mask Layers", "maskLayerNames", hide = True)
        self.newOutput("Boolean List", "Invert Mask Layers", "invertMaskLayers", hide = True)

    def draw(self, layout):
        layout.prop(self, "frameType", text = "")

    def getExecutionFunctionName(self):
        if self.frameType == "ACTIVE":
            return "execute_ActiveFrame"
        elif self.frameType == "INDEX":
            if self.useFrameList:
                return "execute_FrameIndices"
            else:
                return "execute_FrameIndex"
        elif self.frameType == "FRAME":
            if self.useFrameList:
                return "execute_FrameNumbers"
            else:
                return "execute_FrameNumber"
        elif self.frameType == "ALL":
            return "execute_AllFrames"

    def execute_ActiveFrame(self, layer, scene):
        frames = layer.frames
        if len(frames) == 0:
            maskLayerNames, invertMaskLayers = self.getMaskLayers(layer)
            return (GPFrame(), layer.layerName, layer.blendMode, layer.opacity, layer.tintColor,
                    layer.tintFactor, layer.lineChange, layer.passIndex, maskLayerNames, invertMaskLayers)

        maskLayerNames, invertMaskLayers = self.getMaskLayers(layer)
        return (self.getActiveFrame(scene.frame_current, frames), layer.layerName, layer.blendMode,
                layer.opacity, layer.tintColor, layer.tintFactor, layer.lineChange, layer.passIndex,
                maskLayerNames, invertMaskLayers)

    def execute_FrameIndex(self, layer, frameIndex):
        frames = layer.frames
        if len(frames) == 0:
            maskLayerNames, invertMaskLayers = self.getMaskLayers(layer)
            return (GPFrame(), layer.layerName, layer.blendMode, layer.opacity, layer.tintColor,
                    layer.tintFactor, layer.lineChange, layer.passIndex, maskLayerNames, invertMaskLayers)

        frame = self.getFrame(frames, frameIndex)
        maskLayerNames, invertMaskLayers = self.getMaskLayers(layer)
        return (frame, layer.layerName, layer.blendMode, layer.opacity, layer.tintColor,
                layer.tintFactor, layer.lineChange, layer.passIndex, maskLayerNames, invertMaskLayers)

    def execute_FrameIndices(self, layer, frameIndices):
        frames = layer.frames
        if len(frames) == 0:
            maskLayerNames, invertMaskLayers = self.getMaskLayers(layer)
            return ([], layer.layerName, layer.blendMode, layer.opacity, layer.tintColor,
                    layer.tintFactor, layer.lineChange, layer.passIndex, maskLayerNames, invertMaskLayers)

        outFrames = [self.getFrame(frames, index) for index in frameIndices]
        maskLayerNames, invertMaskLayers = self.getMaskLayers(layer)
        return (outFrames, layer.layerName, layer.blendMode, layer.opacity, layer.tintColor,
                layer.tintFactor, layer.lineChange, layer.passIndex, maskLayerNames, invertMaskLayers)

    def execute_FrameNumber(self, layer, frameNumber):
        frames = layer.frames
        if len(frames) == 0:
            maskLayerNames, invertMaskLayers = self.getMaskLayers(layer)
            return (GPFrame(), layer.layerName, layer.blendMode, layer.opacity, layer.tintColor,
                    layer.tintFactor, layer.lineChange, layer.passIndex, maskLayerNames, invertMaskLayers)

        maskLayerNames, invertMaskLayers = self.getMaskLayers(layer)
        return (self.getFrameFromNumber(frames, frameNumber), layer.layerName, layer.blendMode,
                layer.opacity, layer.tintColor, layer.tintFactor, layer.lineChange, layer.passIndex,
                maskLayerNames, invertMaskLayers)

    def execute_FrameNumbers(self, layer, inFrameNumbers):
        frames = layer.frames
        if len(frames) == 0:
            maskLayerNames, invertMaskLayers = self.getMaskLayers(layer)
            return ([], layer.layerName, layer.blendMode, layer.opacity, layer.tintColor,
                    layer.tintFactor, layer.lineChange, layer.passIndex, maskLayerNames, invertMaskLayers)

        outFrames = [self.getFrameFromNumber(frames, frameNumber) for frameNumber in inFrameNumbers]
        maskLayerNames, invertMaskLayers = self.getMaskLayers(layer)
        return (outFrames, layer.layerName, layer.blendMode, layer.opacity, layer.tintColor,
                layer.tintFactor, layer.lineChange, layer.passIndex, maskLayerNames, invertMaskLayers)

    def execute_AllFrames(self, layer):
        frames = layer.frames
        maskLayerNames, invertMaskLayers = self.getMaskLayers(layer)
        return (frames, layer.layerName, layer.blendMode, layer.opacity, layer.tintColor,
                layer.tintFactor, layer.lineChange, layer.passIndex, maskLayerNames, invertMaskLayers)

    def getActiveFrame(self, currentFrame, frames):
        return max((frame for frame in frames if frame.frameNumber <= currentFrame),
                    key = lambda frame : frame.frameNumber, default = frames[0])

    def getFrameFromNumber(self, frames, frameNumber):
        frame = next(filter(lambda f: f.frameNumber == frameNumber, frames), None)
        if frame is None:
            self.raiseErrorMessage(f"There is no frame for frame-number '{frameNumber}'.")
        return frame

    def getFrame(self, frames, frameIndex):
        if frameIndex < 0 or frameIndex >= len(frames):
            self.raiseErrorMessage(f"There is no frame for index '{frameIndex}'.")
        return frames[frameIndex]

    def getMaskLayers(self, layer):
        maskLayers = layer.maskLayers
        return list(maskLayers.keys()), BooleanList.fromListOrTuple(list(maskLayers.values()))
