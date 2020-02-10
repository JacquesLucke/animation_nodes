import bpy
from ... data_structures import VirtualPyList, GPStroke
from ... base_types import AnimationNode, VectorizedSocket

class SetGPStrokeDisplayModeNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_SetGPStrokeDisplayModeNode"
    bl_label = "Set GP Stroke Display Mode"
    errorHandlingType = "EXCEPTION"

    useStrokeList: VectorizedSocket.newProperty()
    useModeTextList: VectorizedSocket.newProperty()

    def create(self):
        self.newInput(VectorizedSocket("GPStroke", "useStrokeList",
            ("Stroke", "stroke"), ("Strokes", "strokes")), dataIsModified = True)
        self.newInput(VectorizedSocket("Text", "useModeTextList",
            ("Display Mode", "displayMode"), ("Display Modes", "displayModes")), value = "3DSPACE")
        self.newOutput(VectorizedSocket("GPStroke", ["useStrokeList", "useModeTextList"],
            ("Stroke", "outStroke"), ("Strokes", "outStrokes")))

    def getExecutionFunctionName(self):
        if self.useStrokeList or self.useModeTextList:
            return "execute_StrokeList_DisplayModeList"
        else:
            return "execute_Stroke_DisplayMode"

    def execute_Stroke_DisplayMode(self, stroke, displayMode):
        return self.setStrokeDisplayMode(stroke, displayMode)

    def execute_StrokeList_DisplayModeList(self, strokes, displayModes):
        _strokes = VirtualPyList.create(strokes, GPStroke())
        _displayModes = VirtualPyList.create(displayModes, "3DSPACE")
        amount = VirtualPyList.getMaxRealLength(_strokes, _displayModes)

        outStrokes = []
        for i in range(amount):
            strokeNew = _strokes[i].copy()
            self.setStrokeDisplayMode(strokeNew, _displayModes[i])
            outStrokes.append(strokeNew)
        return outStrokes

    def setStrokeDisplayMode(self, stroke, displayMode):
        if displayMode not in ['SCREEN', '3DSPACE', '2DSPACE', '2DIMAGE']:
            self.raiseErrorMessage("The Display Mode is invalid. \n\nPossible values for 'Display Mode' are: 'SCREEN', '3DSPACE', '2DSPACE', '2DIMAGE'")

        stroke.displayMode = displayMode
        return stroke
