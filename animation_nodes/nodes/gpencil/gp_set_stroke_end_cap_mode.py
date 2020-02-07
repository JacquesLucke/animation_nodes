import bpy
from ... data_structures import VirtualPyList
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
            ("Stroke", "stroke"), ("Strokes", "strokes")))

    def getExecutionFunctionName(self):
        if self.useStrokeList and self.useModeTextList:
            return "execute_StrokeList_EndCapModeList"
        elif self.useStrokeList:
            return "execute_StrokeList_EndCapMode"
        elif self.useModeTextList:
            return "execute_Stroke_EndCapModeList"
        else:
            return "execute_Stroke_EndCapMode"

    def execute_Stroke_EndCapMode(self, stroke, endCapMode):
        self.setStrokeEndCapMode(stroke, endCapMode)
        return stroke

    def execute_Stroke_EndCapModeList(self, stroke, endCapModes):
        if len(endCapModes) == 0: return [stroke]

        strokes = []
        for endCapMode in endCapModes:
            strokeNew = stroke.copy()
            self.setStrokeEndCapMode(strokeNew, endCapMode)
            strokes.append(strokeNew)
        return strokes

    def execute_StrokeList_EndCapMode(self, strokes, endCapMode):
        if len(strokes) == 0: return strokes
        for stroke in strokes:
            self.setStrokeEndCapMode(stroke, endCapMode)
        return strokes

    def execute_StrokeList_EndCapModeList(self, strokes, endCapModes):
        endCapModes = VirtualPyList.create(endCapModes, "ROUND")
        for i, stroke in enumerate(strokes):
            self.setStrokeEndCapMode(stroke, endCapModes[i])
        return strokes

    def setStrokeEndCapMode(self, stroke, endCapMode):
        if endCapMode not in ['ROUND', 'FLAT']:
            self.raiseErrorMessage("The End Cap Mode is invalid. \n\nPossible values for 'End Cap Mode' are: 'ROUND', 'FLAT'")

        stroke.endCapMode = endCapMode
        return stroke
