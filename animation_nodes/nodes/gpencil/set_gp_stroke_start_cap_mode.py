import bpy
from ... data_structures import VirtualPyList, GPStroke
from ... base_types import AnimationNode, VectorizedSocket

class SetGPStrokeStartCapModeNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_SetGPStrokeStartCapModeNode"
    bl_label = "Set GP Stroke Start Cap Mode"
    errorHandlingType = "EXCEPTION"

    useStrokeList: VectorizedSocket.newProperty()
    useModeTextList: VectorizedSocket.newProperty()

    def create(self):
        self.newInput(VectorizedSocket("GPStroke", "useStrokeList",
            ("Stroke", "stroke"), ("Strokes", "strokes")), dataIsModified = True)
        self.newInput(VectorizedSocket("Text", "useModeTextList",
            ("Start Cap Mode", "startCapMode"), ("Start Cap Modes", "startCapModes")), value = "ROUND")
        self.newOutput(VectorizedSocket("GPStroke", ["useStrokeList", "useModeTextList"],
            ("Stroke", "stroke"), ("Strokes", "strokes")))

    def getExecutionFunctionName(self):
        if self.useStrokeList or self.useModeTextList:
            return "execute_StrokeList_StartCapModeList"
        else:
            return "execute_Stroke_StartCapMode"

    def execute_Stroke_StartCapMode(self, stroke, startCapMode):
        self.setStrokeStartCapMode(stroke, startCapMode)
        return stroke

    def execute_StrokeList_StartCapModeList(self, strokes, startCapModes):
        _strokes = VirtualPyList.create(strokes, GPStroke())
        _startCapModes = VirtualPyList.create(startCapModes, "ROUND")
        amount = VirtualPyList.getMaxRealLength(_strokes, _startCapModes)

        outStrokes = []
        for i in range(amount):
            strokeNew = _strokes[i].copy()
            self.setStrokeStartCapMode(strokeNew, _startCapModes[i])
            outStrokes.append(strokeNew)
        return outStrokes

    def setStrokeStartCapMode(self, stroke, startCapMode):
        if startCapMode not in ['ROUND', 'FLAT']:
            self.raiseErrorMessage("The Start Cap Mode is invalid. \n\nPossible values for 'Start Cap Mode' are: 'ROUND', 'FLAT'")

        stroke.startCapMode = startCapMode
        return stroke
