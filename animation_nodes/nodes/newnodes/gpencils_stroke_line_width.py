import bpy
from ... base_types import AnimationNode, VectorizedSocket

class GPencilStrokeLineWidthNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_GPencilStrokeLineWidthNode"
    bl_label = "GPencil Stroke Line Width"
    bl_width_default = 165

    useStrokeList: VectorizedSocket.newProperty()
    useFloatList: VectorizedSocket.newProperty()

    def create(self):
        self.newInput(VectorizedSocket("Stroke", "useStrokeList",
            ("Stroke", "stroke"), ("Strokes", "strokes")), dataIsModified = True)
        self.newInput(VectorizedSocket("Float", "useFloatList",
            ("Line Width", "lineWidth"), ("Line Widths", "lineWidths")), value = 100)
        self.newOutput(VectorizedSocket("Stroke", "useStrokeList",
            ("Stroke", "outStroke"), ("Strokes", "outStrokes")), dataIsModified = True)

    def getExecutionFunctionName(self):
        if self.useStrokeList and self.useFloatList:
            return "executeListList"
        elif self.useStrokeList:
            return "executeList"
        else:
            return "executeSingle"

    def executeSingle(self, stroke, lineWidth):
        if stroke is None: return None
        stroke.line_width = lineWidth
        return stroke

    def executeList(self, strokes, lineWidth):
        if len(strokes) == 0: return strokes
        for stroke in strokes:
            if stroke is not None:
                stroke.line_width = lineWidth
        return strokes

    def executeListList(self, strokes, lineWidths):
        if len(strokes) == 0 or len(lineWidths) == 0 or len(strokes) != len(lineWidths): return strokes
        for i, stroke in enumerate(strokes):
            if stroke is not None:
                stroke.line_width = lineWidths[i]
        return strokes