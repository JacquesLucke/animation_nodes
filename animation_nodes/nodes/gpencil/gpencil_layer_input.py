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

class GPencilLayerInputNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_GPencilLayerInputNode"
    bl_label = "GPencil Layer Input"
    errorHandlingType = "EXCEPTION"

    frameType: EnumProperty(name = "Frame Type", default = "ACTIVE",
        items = frameTypeItems, update = AnimationNode.refresh)

    useFrameList: VectorizedSocket.newProperty()

    def create(self):
        self.newInput("GPLayer", "GPencil Layer", "layer", dataIsModified = True)

        if self.frameType == "ACTIVE":
            self.newInput("Scene", "Scene", "scene", hide = True)

            self.newOutput("GPFrame", "Frame", "frame")
            self.newOutput("Integer", "Frame Index", "frameIndex")
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
            self.newOutput(VectorizedSocket("Integer", "useFrameList",
            ("Frame Index", "frameIndex"), ("Frame Indices", "outframeIndices")))
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
            return GPFrame(), 0, 0, layer.layerName, layer.blendMode, layer.opacity, layer.passIndex
        frameNumbers = layer.frameNumbers
        activeIndex = self.getActiveFrameIndex(scene.frame_current, frameNumbers)
        return frames[activeIndex], activeIndex, frameNumbers[activeIndex], layer.layerName,\
               layer.blendMode, layer.opacity, layer.passIndex

    def execute_FrameIndex(self, layer, frameIndex):
        frames = layer.frames
        if len(layer.frames) == 0:
            return GPFrame(), 0, layer.layerName, layer.blendMode, layer.opacity, layer.passIndex
        frame = self.getFrame(frames, frameIndex)
        frameNumbers = layer.frameNumbers
        return frame, frameNumbers[frameIndex], layer.layerName, layer.blendMode, layer.opacity, layer.passIndex

    def execute_FrameIndices(self, layer, frameIndices):
        frames = layer.frames
        outFrames = []
        if len(layer.frames) == 0:
            return outFrames, LongList(), layer.layerName, layer.blendMode, layer.opacity, layer.passIndex
        frameNumbers = layer.frameNumbers
        outFrameNumbers = LongList(length = len(frameIndices))
        for i, index in enumerate(frameIndices):
            outFrames.append(self.getFrame(frames, index))
            outFrameNumbers[i] = frameNumbers[index]
        return outFrames, outFrameNumbers, layer.layerName, layer.blendMode, layer.opacity, layer.passIndex

    def execute_FrameNumber(self, layer, frameNumber):
        frames = layer.frames
        if len(layer.frames) == 0:
            return GPFrame(), 0, layer.layerName, layer.blendMode, layer.opacity, layer.passIndex
        frameNumbers = layer.frameNumbers
        index = self.getFrameNumberIndex(frameNumbers, frameNumber)
        return frames[index], index, layer.layerName, layer.blendMode, layer.opacity, layer.passIndex

    def execute_FrameNumbers(self, layer, inframeNumbers):
        frames = layer.frames
        outFrames = []
        if len(layer.frames) == 0:
            return outFrames, LongList(), layer.layerName, layer.blendMode, layer.opacity, layer.passIndex
        frameNumbers = layer.frameNumbers
        outFrameIndices = LongList(length = len(frameNumbers))
        for i, frameNumber in enumerate(inframeNumbers):
            index = self.getFrameNumberIndex(frameNumbers, frameNumber)
            outFrames.append(frames[index])
            outFrameIndices[i] = index
        return outFrames, outFrameIndices, layer.layerName, layer.blendMode, layer.opacity, layer.passIndex

    def execute_AllFrames(self, layer):
        return layer.frames, layer.frameNumbers, layer.layerName, layer.blendMode, layer.opacity, layer.passIndex

    def getActiveFrameIndex(self, currentFrame, frameNumbers):
        minFrame = frameNumbers.getMinValue()
        if currentFrame <= minFrame: return 0
        allFrames = list(filter(lambda x: x <= currentFrame, frameNumbers))
        return frameNumbers.index(allFrames[-1])

    def getFrameNumberIndex(self, frameNumbers, frameNumber):
        try: return frameNumbers.index(frameNumber)
        except: self.raiseErrorMessage(f"There is no frame for frame-number '{frameNumber}'.")

    def getFrame(self, frames, frameIndex):
        try: return frames[frameIndex]
        except: self.raiseErrorMessage(f"There is no frame for index '{frameIndex}'.")
