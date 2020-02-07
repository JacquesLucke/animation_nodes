import bpy
from ... data_structures import VirtualDoubleList
from ... base_types import AnimationNode, VectorizedSocket

class GPSetStrokeLineWidthNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_GPSetStrokeLineWidthNode"
    bl_label = "GP Set Stroke Line Width"

    useStrokeList: VectorizedSocket.newProperty()
    useFloatList: VectorizedSocket.newProperty()

    def create(self):
        self.newInput(VectorizedSocket("GPStroke", "useStrokeList",
            ("Stroke", "stroke"), ("Strokes", "strokes")), dataIsModified = True)
        self.newInput(VectorizedSocket("Float", "useFloatList",
            ("Line Width", "lineWidth"), ("Line Widths", "lineWidths")), value = 250)
        self.newOutput(VectorizedSocket("GPStroke", ["useStrokeList", "useFloatList"],
            ("Stroke", "outStroke"), ("Strokes", "outStrokes")))

    def getExecutionFunctionName(self):
        if self.useStrokeList and self.useFloatList:
            return "execute_StrokeList_LineWidthList"
        elif self.useStrokeList:
            return "execute_StrokeList_LineWidth"
        elif self.useFloatList:
            return "execute_Stroke_LineWidthList"
        else:
            return "execute_Stroke_LineWidth"

    def execute_Stroke_LineWidth(self, stroke, lineWidth):
        stroke.lineWidth = lineWidth
        return stroke

    def execute_Stroke_LineWidthList(self, stroke, lineWidths):
        if len(lineWidths) == 0: return [stroke]
        strokes = []
        for lineWidth in lineWidths:
            strokeNew = stroke.copy()
            strokeNew.lineWidth = lineWidth
            strokes.append(strokeNew)
        return strokes

    def execute_StrokeList_LineWidth(self, strokes, lineWidth):
        if len(strokes) == 0: return strokes
        for stroke in strokes:
            stroke.lineWidth = lineWidth
        return strokes

    def execute_StrokeList_LineWidthList(self, strokes, lineWidths):
        if len(strokes) == 0 or len(lineWidths) == 0: return strokes
        lineWidths = VirtualDoubleList.create(lineWidths, 0)
        for i, stroke in enumerate(strokes):
            stroke.lineWidth = lineWidths[i]
        return strokes
