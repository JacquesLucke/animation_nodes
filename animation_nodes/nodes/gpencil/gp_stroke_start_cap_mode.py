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
        self.strokeStartCapMode(stroke, startCapMode)
        return stroke

    def execute_StrokeList_StartCapMode(self, strokes, startCapMode):
        if len(strokes) == 0: return strokes
        for stroke in strokes:
            self.strokeStartCapMode(stroke, startCapMode)
        return strokes

    def execute_StrokeList_StartCapModeList(self, strokes, startCapModes):
        if len(strokes) == 0 or len(startCapModes) == 0: return strokes
        if len(strokes) < len(startCapModes):
            self.raiseErrorMessage("Invalid stroke list.")
        if len(strokes) > len(startCapModes):
            self.raiseErrorMessage("Invalid start cap mode list.")
        for i, stroke in enumerate(strokes):
            self.strokeStartCapMode(stroke, startCapModes[i])
        return strokes

    def strokeStartCapMode(self, stroke, startCapMode):
        if startCapMode not in ['ROUND', 'FLAT']:
            self.raiseErrorMessage("The Start Cap mode is invalid. \n\nPossible values for 'Start Cap Mode' are: 'REGULAR', 'FLAT'")

        stroke.startCapMode = startCapMode
        return stroke
