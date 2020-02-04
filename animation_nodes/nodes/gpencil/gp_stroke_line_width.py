import bpy
from ... data_structures import VirtualDoubleList
from ... base_types import AnimationNode, VectorizedSocket

class GPStrokeLineWidthNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_GPStrokeLineWidthNode"
    bl_label = "GP Stroke Line Width"

    useStrokeList: VectorizedSocket.newProperty()
    useFloatList: VectorizedSocket.newProperty()

    def create(self):
        self.newInput(VectorizedSocket("GPStroke", "useStrokeList",
            ("Stroke", "stroke"), ("Strokes", "strokes")), dataIsModified = True)
        self.newInput(VectorizedSocket("Float", "useFloatList",
            ("Line Width", "lineWidth"), ("Line Widths", "lineWidths")), value = 250)
        self.newOutput(VectorizedSocket("GPStroke", "useStrokeList",
            ("Stroke", "outStroke"), ("Strokes", "outStrokes")))

    def getExecutionFunctionName(self):
        if self.useStrokeList and self.useFloatList:
            return "executeListList"
        elif self.useStrokeList:
            return "executeList"
        else:
            return "executeSingle"

    def executeSingle(self, stroke, lineWidth):
        stroke.lineWidth = lineWidth
        return stroke

    def executeList(self, strokes, lineWidth):
        if len(strokes) == 0: return strokes
        for stroke in strokes:
            stroke.lineWidth = lineWidth
        return strokes

    def executeListList(self, strokes, lineWidths):
        if len(strokes) == 0 or len(lineWidths) == 0: return strokes
        lineWidths = VirtualDoubleList.create(lineWidths, 0)
        for i, stroke in enumerate(strokes):
            stroke.lineWidth = lineWidths[i]
        return strokes
