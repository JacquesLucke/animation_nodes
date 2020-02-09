import bpy
from ... data_structures import VirtualPyList, GPStroke
from ... base_types import AnimationNode, VectorizedSocket

class GPSetStrokeEndCapModeNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_GPSetStrokeEndCapModeNode"
    bl_label = "GP Set Stroke End Cap Mode"
    errorHandlingType = "EXCEPTION"

    useStrokeList: VectorizedSocket.newProperty()
    useModeTextList: VectorizedSocket.newProperty()

    def create(self):
        self.newInput(VectorizedSocket("GPStroke", "useStrokeList",
            ("Stroke", "stroke"), ("Strokes", "strokes")), dataIsModified = True)
        self.newInput(VectorizedSocket("Text", "useModeTextList",
            ("End Cap Mode", "endCapMode"), ("End Cap Modes", "endCapModes")), value = "ROUND")
        self.newOutput(VectorizedSocket("GPStroke", ["useStrokeList", "useModeTextList"],
            ("Stroke", "outStroke"), ("Strokes", "outStrokes")))

    def getExecutionFunctionName(self):
        if self.useStrokeList or self.useModeTextList:
            return "execute_StrokeList_EndCapModeList"
        else:
            return "execute_Stroke_EndCapMode"

    def execute_Stroke_EndCapMode(self, stroke, endCapMode):
        self.setStrokeEndCapMode(stroke, endCapMode)
        return stroke

    def execute_StrokeList_EndCapModeList(self, strokes, endCapModes):
        _strokes = VirtualPyList.create(strokes, GPStroke())
        _endCapModes = VirtualPyList.create(endCapModes, "ROUND")
        amount = VirtualPyList.getMaxRealLength(_strokes, _endCapModes)

        outStrokes = []
        for i in range(amount):
            strokeNew = _strokes[i].copy()
            self.setStrokeEndCapMode(strokeNew, _endCapModes[i])
            outStrokes.append(strokeNew)
        return outStrokes

    def setStrokeEndCapMode(self, stroke, endCapMode):
        if endCapMode not in ['ROUND', 'FLAT']:
            self.raiseErrorMessage("The End Cap Mode is invalid. \n\nPossible values for 'End Cap Mode' are: 'ROUND', 'FLAT'")

        stroke.endCapMode = endCapMode
        return stroke
