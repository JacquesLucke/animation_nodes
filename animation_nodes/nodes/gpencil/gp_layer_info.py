import bpy
from bpy.props import *
from ... events import propertyChanged
from ... data_structures import GPFrame, LongList
from ... base_types import AnimationNode, VectorizedSocket

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
            self.newOutput("Float", "Frame Number", "frameNumber")

        elif self.frameType == "INDEX":
            self.newInput(VectorizedSocket("Integer", "useFrameList",
            ("Frame Index", "frameIndex"), ("Frame Indices", "frameIndices")))
            self.newOutput(VectorizedSocket("GPFrame", "useFrameList",
            ("Frame", "frame"), ("Frames", "frames")))
            self.newOutput(VectorizedSocket("Float", "useFrameList",
            ("Frame Number", "frameNumber"), ("Frame Numbers", "outframeNumbers")))

        elif self.frameType == "FRAME":
            self.newInput(VectorizedSocket("Float", "useFrameList",
            ("Frame Number", "frameNumber"), ("Frame Numbers", "inframeNumbers")))
            self.newOutput(VectorizedSocket("GPFrame", "useFrameList",
            ("Frame", "frame"), ("Frames", "frames")))

        elif self.frameType == "ALL":
            self.newOutput("GPFrame List", "Frames", "frames")
            self.newOutput("Float List", "Frame Numbers", "outframeNumbers")

        self.newOutput("Text", "Layer Name", "layerName", hide = True)
        self.newOutput("Text", "Layer Blend Mode", "blendMode", hide = True)
        self.newOutput("Float", "Layer Opacity", "opacity", hide = True)
        self.newOutput("Integer", "Layer Pass Index", "passIndex", hide = True)

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
        if len(layer.frames) == 0:
            return GPFrame(), 0, layer.layerName, layer.blendMode, layer.opacity, layer.passIndex

        frameNumbers = self.getFrameNumbers(frames)
        activeIndex = self.getActiveFrameIndex(scene.frame_current, frameNumbers)
        return (frames[activeIndex], frameNumbers[activeIndex], layer.layerName, layer.blendMode,
                layer.opacity, layer.passIndex)

    def execute_FrameIndex(self, layer, frameIndex):
        frames = layer.frames
        if len(layer.frames) == 0:
            return GPFrame(), 0, layer.layerName, layer.blendMode, layer.opacity, layer.passIndex

        frame = self.getFrame(frames, frameIndex)
        return frame, frame.frameNumber, layer.layerName, layer.blendMode, layer.opacity, layer.passIndex

    def execute_FrameIndices(self, layer, frameIndices):
        frames = layer.frames
        outFrames = []
        if len(layer.frames) == 0:
            return outFrames, LongList(), layer.layerName, layer.blendMode, layer.opacity, layer.passIndex

        frameNumbers = self.getFrameNumbers(frames)
        outFrameNumbers = LongList(length = len(frameIndices))
        for i, index in enumerate(frameIndices):
            outFrames.append(self.getFrame(frames, index))
            outFrameNumbers[i] = frameNumbers[index]
        return outFrames, outFrameNumbers, layer.layerName, layer.blendMode, layer.opacity, layer.passIndex

    def execute_FrameNumber(self, layer, frameNumber):
        frames = layer.frames
        if len(layer.frames) == 0:
            return GPFrame(), layer.layerName, layer.blendMode, layer.opacity, layer.passIndex

        frameNumbers = self.getFrameNumbers(frames)
        index = self.getFrameNumberIndex(frameNumbers, frameNumber)
        return frames[index], layer.layerName, layer.blendMode, layer.opacity, layer.passIndex

    def execute_FrameNumbers(self, layer, inframeNumbers):
        frames = layer.frames
        outFrames = []
        if len(layer.frames) == 0:
            return outFrames, LongList(), layer.layerName, layer.blendMode, layer.opacity, layer.passIndex

        frameNumbers = self.getFrameNumbers(frames)
        for frameNumber in inframeNumbers:
            index = self.getFrameNumberIndex(frameNumbers, frameNumber)
            outFrames.append(frames[index])
        return outFrames, layer.layerName, layer.blendMode, layer.opacity, layer.passIndex

    def execute_AllFrames(self, layer):
        frames = layer.frames
        return frames, self.getFrameNumbers(frames), layer.layerName, layer.blendMode, layer.opacity, layer.passIndex

    def getActiveFrameIndex(self, currentFrame, frameNumbers):
        minFrame = frameNumbers.getMinValue()
        if currentFrame <= minFrame: return 0
        allFrames = list(filter(lambda x: x <= currentFrame, frameNumbers))
        return frameNumbers.index(allFrames[-1])

    def getFrameNumbers(self, frames):
        frameNumbers = LongList(length = len(frames))
        for i, frame in enumerate(frames):
            frameNumbers[i] = frame.frameNumber
        return frameNumbers

    def getFrameNumberIndex(self, frameNumbers, frameNumber):
        if frameNumber not in set(frameNumbers):
            self.raiseErrorMessage(f"There is no frame for frame-number '{frameNumber}'.")
        return frameNumbers.index(frameNumber)

    def getFrame(self, frames, frameIndex):
        if frameIndex < 0 or frameIndex >= len(frames):
            self.raiseErrorMessage(f"There is no frame for index '{frameIndex}'.")
        return frames[frameIndex]
