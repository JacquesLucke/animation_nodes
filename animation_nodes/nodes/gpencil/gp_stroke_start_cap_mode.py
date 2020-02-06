import bpy
from ... base_types import AnimationNode, VectorizedSocket

class GPStrokeStartCapModeNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_GPStrokeStartCapModeNode"
    bl_label = "GP Stroke Start Cap Mode"
    errorHandlingType = "EXCEPTION"

    useStrokeList: VectorizedSocket.newProperty()
    useModeTextList: VectorizedSocket.newProperty()

    def create(self):
        self.newInput(VectorizedSocket("GPStroke", "useStrokeList",
            ("Stroke", "stroke"), ("Strokes", "strokes")), dataIsModified = True)
        self.newInput(VectorizedSocket("Text", ["useStrokeList", "useModeTextList"],
            ("Start Cap Mode", "startCapMode"), ("Start Cap Modes", "startCapModes")), value = "ROUND")
        self.newOutput(VectorizedSocket("GPStroke", "useStrokeList",
            ("Stroke", "stroke"), ("Strokes", "strokes")))

    def getExecutionFunctionName(self):
        if self.useStrokeList and self.useModeTextList:
            return "execute_StrokeList_StartCapModeList"
        elif self.useStrokeList:
            return "execute_StrokeList_StartCapMode"
        else:
            return "execute_Stroke_StartCapMode"

    def execute_Stroke_StartCapMode(self, stroke, startCapMode):
        self.setStrokeStartCapMode(stroke, startCapMode)
        return stroke

    def execute_StrokeList_StartCapMode(self, strokes, startCapMode):
        if len(strokes) == 0: return strokes
        for stroke in strokes:
            self.setStrokeStartCapMode(stroke, startCapMode)
        return strokes

    def execute_StrokeList_StartCapModeList(self, strokes, startCapModes):
        if len(strokes) == 0 or len(startCapModes) == 0: return strokes
        if len(strokes) != len(startCapModes):
            self.raiseErrorMessage("Strokes and Start Cap Modes have different lengths.")
        for i, stroke in enumerate(strokes):
            self.strokeStartCapMode(stroke, startCapModes[i])
        return strokes

    def setStrokeStartCapMode(self, stroke, startCapMode):
        if startCapMode not in ['ROUND', 'FLAT']:
            self.raiseErrorMessage("The Start Cap Mode is invalid. \n\nPossible values for 'Start Cap Mode' are: 'ROUND', 'FLAT'")

        stroke.startCapMode = startCapMode
        return stroke
