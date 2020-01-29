import bpy
import numpy as np
from bpy.props import *
from ... data_structures import Frame
from ... events import propertyChanged
from ... base_types import AnimationNode, VectorizedSocket

class GPencilFrameOutputNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_GPencilFrameOutputNode"
    bl_label = "GPencil Frame Output"
    errorHandlingType = "EXCEPTION"

    useStrokeList: VectorizedSocket.newProperty()
    useNumberList: VectorizedSocket.newProperty()

    def create(self):
        self.newInput(VectorizedSocket("Stroke", "useStrokeList",
            ("Stroke", "stroke"), ("Strokes", "strokes")), dataIsModified = True)
        self.newInput(VectorizedSocket("Float", "useNumberList",
            ("Frame Number", "frameNumber"), ("Frame Numbers", "frameNumbers")), dataIsModified = True)
        self.newOutput(VectorizedSocket("Frame", "useNumberList",
            ("Frame", "frame"), ("Frames", "frames")))

    def getExecutionFunctionName(self):
        if self.useNumberList:
            return "execute_StrokesFrameNumbers"
        else:
            return "execute_StrokesFrameNumber"

    def execute_StrokesFrameNumber(self, strokes, frameNumber):
        if not self.useStrokeList:
            strokes = [strokes]

        return Frame(strokes, 0, frameNumber)

    def execute_StrokesFrameNumbers(self, strokes, frameNumbers):
        frames = []
        if not self.useStrokeList:
            return frames

        if len(strokes) > len(frameNumbers):
            self.raiseErrorMessage("Invalid Frame Numbers list.")

        if len(np.unique(frameNumbers)) != len(frameNumbers):
            self.raiseErrorMessage("Some Frame Numbers are repeated.")

        for i, stroke in enumerate(strokes):
            frames.append(Frame([stroke], i, frameNumbers[i]))
        return frames
