import bpy
from ... data_structures import VirtualPyList
from ... base_types import AnimationNode, VectorizedSocket

class GPSetStrokeDisplayModeNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_GPSetStrokeDisplayModeNode"
    bl_label = "GP Set Stroke Display Mode"
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
        if self.useStrokeList and self.useModeTextList:
            return "execute_StrokeList_DisplayModeList"
        elif self.useStrokeList:
            return "execute_StrokeList_DisplayMode"
        elif self.useModeTextList:
            return "execute_Stroke_DisplayModeList"
        else:
            return "execute_Stroke_DisplayMode"

    def execute_Stroke_DisplayMode(self, stroke, displayMode):
        return self.setStrokeDisplayMode(stroke, displayMode)

    def execute_Stroke_DisplayModeList(self, stroke, displayModes):
        if len(displayModes) == 0: return [stroke]

        strokes = []
        for displayMode in displayModes:
            strokeNew = stroke.copy()
            self.setStrokeDisplayMode(strokeNew, displayMode)
            strokes.append(strokeNew)
        return strokes

    def execute_StrokeList_DisplayMode(self, strokes, displayMode):
        if len(strokes) == 0: return strokes
        for stroke in strokes:
            self.setStrokeDisplayMode(stroke, displayMode)
        return strokes

    def execute_StrokeList_DisplayModeList(self, strokes, displayModes):
        displayModes = VirtualPyList.create(displayModes, "3DSPACE")
        for i, stroke in enumerate(strokes):
            displayMode = displayModes[i]
            self.setStrokeDisplayMode(stroke, displayMode)
        return strokes

    def setStrokeDisplayMode(self, stroke, displayMode):
        if displayMode not in ['SCREEN', '3DSPACE', '2DSPACE', '2DIMAGE']:
            self.raiseErrorMessage("The Display Mode is invalid. \n\nPossible values for 'Display Mode' are: 'SCREEN', '3DSPACE', '2DSPACE', '2DIMAGE'")

        stroke.displayMode = displayMode
        return stroke
