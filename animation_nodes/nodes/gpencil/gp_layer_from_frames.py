import bpy
import numpy as np
from bpy.props import *
from ... events import propertyChanged
from ... data_structures import GPLayer, LongList
from ... base_types import AnimationNode, VectorizedSocket

class GPLayerFromFramesNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_GPLayerFromFramesNode"
    bl_label = "GP Layer From Frames"
    errorHandlingType = "EXCEPTION"

    useFrameList: VectorizedSocket.newProperty()
    useGPFrameList: VectorizedSocket.newProperty()

    def create(self):
        self.newInput(VectorizedSocket("GPFrame", "useFrameList",
            ("Frame", "frame"), ("Frames", "frames")), dataIsModified = True)
        self.newInput("Text", "Name", "layerName", value = 'AN-Layer')
        self.newInput("Text", "Blend Mode", "blendMode", value = 'REGULAR', hide = True)
        self.newInput("Float", "Opacity", "opacity", value = 1, hide = True)
        self.newInput("Integer", "Pass Index", "passIndex", value = 0, hide = True)
        self.newOutput("GPLayer", "GPencil Layer", "gpencilLayer")

    def execute(self, frames, layerName, blendMode, opacity, passIndex):
        if not self.useFrameList:
            frames = [frames]

        frameNumbers = LongList(length = len(frames))
        for i, frame in enumerate(frames):
            frameNumbers[i] = frame.frameNumber
        if len(np.unique(frameNumbers)) != len(frameNumbers):
            self.raiseErrorMessage("Some Frame Numbers are repeated.")
        if blendMode not in ['REGULAR', 'OVERLAY', 'ADD', 'SUBTRACT', 'MULTIPLY', 'DIVIDE']:
            self.raiseErrorMessage("The blend mode is invalid. \n\nPossible values for 'Blend Mode' are: 'REGULAR', 'OVERLAY', 'ADD', 'SUBTRACT', 'MULTIPLY', 'DIVIDE'")
        return GPLayer(layerName, frames, frameNumbers, blendMode, opacity, passIndex)
