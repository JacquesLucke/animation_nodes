import bpy
from ... base_types import AnimationNode, VectorizedSocket

class GPStrokeEndCapModeNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_GPStrokeEndCapModeNode"
    bl_label = "GP Stroke End Cap Mode"
    errorHandlingType = "EXCEPTION"

    useStrokeList: VectorizedSocket.newProperty()
    useModeTextList: VectorizedSocket.newProperty()

    def create(self):
        self.newInput(VectorizedSocket("GPStroke", "useStrokeList",
            ("Stroke", "stroke"), ("Strokes", "strokes")), dataIsModified = True)
        self.newInput(VectorizedSocket("Text", ["useStrokeList", "useModeTextList"],
            ("End Cap Mode", "endCapMode"), ("End Cap Modes", "endCapModes")), value = "ROUND")
        self.newOutput(VectorizedSocket("GPStroke", "useStrokeList",
            ("Stroke", "stroke"), ("Strokes", "strokes")))

    def getExecutionFunctionName(self):
        if self.useStrokeList and self.useModeTextList:
            return "execute_StrokeList_EndCapModeList"
        elif self.useStrokeList:
            return "execute_StrokeList_EndCapMode"
        else:
            return "execute_Stroke_EndCapMode"

    def execute_Stroke_EndCapMode(self, stroke, endCapMode):
        self.strokeEndCapMode(stroke, endCapMode)
        return stroke

    def execute_StrokeList_EndCapMode(self, strokes, endCapMode):
        if len(strokes) == 0: return strokes
        for stroke in strokes:
            self.strokeEndCapMode(stroke, endCapMode)
        return strokes

    def execute_StrokeList_EndCapModeList(self, strokes, endCapModes):
        if len(strokes) == 0 or len(endCapModes) == 0: return strokes
        if len(strokes) < len(endCapModes):
            self.raiseErrorMessage("Invalid stroke list.")
        if len(strokes) > len(endCapModes):
            self.raiseErrorMessage("Invalid end cap mode list.")
        for i, stroke in enumerate(strokes):
            self.strokeEndCapMode(stroke, endCapModes[i])
        return strokes

    def strokeEndCapMode(self, stroke, endCapMode):
        if endCapMode not in ['ROUND', 'FLAT']:
            self.raiseErrorMessage("The End Cap mode is invalid. \n\nPossible values for 'End Cap Mode' are: 'REGULAR', 'FLAT'")

        stroke.endCapMode = endCapMode
        return stroke
