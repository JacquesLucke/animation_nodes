import bpy
import numpy as np
from bpy.props import *
from ... events import propertyChanged
from ... data_structures import GPFrame
from ... base_types import AnimationNode, VectorizedSocket

class GPFrameFromStrokesNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_GPFrameFromStrokesNode"
    bl_label = "GP Frame From Strokes"
    errorHandlingType = "EXCEPTION"

    useStrokeList: VectorizedSocket.newProperty()
    useNumberList: VectorizedSocket.newProperty()

    def create(self):
        self.newInput(VectorizedSocket("GPStroke", "useStrokeList",
            ("Stroke", "stroke"), ("Strokes", "strokes")), dataIsModified = True)
        self.newInput(VectorizedSocket("Integer", ["useStrokeList", "useNumberList"],
            ("Frame Number", "frameNumber"), ("Frame Numbers", "frameNumbers")), value = 1)
        self.newOutput(VectorizedSocket("GPFrame", "useNumberList",
            ("Frame", "frame"), ("Frames", "frames")))

    def getExecutionFunctionName(self):
        if self.useNumberList:
            return "execute_StrokesFrameNumbers"
        else:
            return "execute_StrokesFrameNumber"

    def execute_StrokesFrameNumber(self, strokes, frameNumber):
        if not self.useStrokeList:
            strokes = [strokes]

        return GPFrame(strokes, frameNumber)

    def execute_StrokesFrameNumbers(self, strokes, frameNumbers):
        if len(strokes) != len(frameNumbers):
            self.raiseErrorMessage("Strokes and Frame Numbers have different lengths.")
        if len(np.unique(frameNumbers.asNumpyArray())) != len(frameNumbers):
            self.raiseErrorMessage("Some Frame Numbers are repeated.")

        frames = [GPFrame([stroke], number) for stroke, number in zip(strokes, frameNumbers)]
        return frames
