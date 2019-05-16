import bpy
from ... data_structures import Stroke
from ... base_types import AnimationNode, VectorizedSocket

class GPencilStrokeLineWidthNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_GPencilStrokeLineWidthNode"
    bl_label = "GPencil Stroke Line Width"
    bl_width_default = 165

    useStrokeList: VectorizedSocket.newProperty()
    useFloatList: VectorizedSocket.newProperty()

    def create(self):
        self.newInput(VectorizedSocket("Stroke", "useStrokeList",
            ("Stroke", "stroke"), ("Strokes", "strokes")))
        self.newInput(VectorizedSocket("Float", "useFloatList",
            ("Line Width", "lineWidth"), ("Line Widths", "lineWidths")), value = 100)
        self.newOutput(VectorizedSocket("Stroke", "useStrokeList",
            ("Stroke", "outStroke"), ("Strokes", "outStrokes")))

    def getExecutionFunctionName(self):
        if self.useStrokeList and self.useFloatList:
            return "executeListList"
        elif self.useStrokeList:
            return "executeList"
        else:
            return "executeSingle"

    def executeSingle(self, stroke, lineWidth):
        if stroke is None: return None
        outStroke = self.copyStroke(stroke)
        outStroke.line_width = lineWidth
        return outStroke

    def executeList(self, strokes, lineWidth):
        if len(strokes) == 0: return strokes
        outStrokes = []
        for stroke in strokes:
            if stroke is not None:
                outStroke = self.copyStroke(stroke)
                outStroke.line_width = lineWidth
                outStrokes.append(outStroke)    
        return outStrokes

    def executeListList(self, strokes, lineWidths):
        if len(strokes) == 0 or len(lineWidths) == 0 or len(strokes) != len(lineWidths): return strokes
        outStrokes = []
        for i, stroke in enumerate(strokes):
            if stroke is not None:
                outStroke = self.copyStroke(stroke)
                outStroke.line_width = lineWidths[i]
                outStrokes.append(outStroke)
        return outStrokes

    def copyStroke(self, stroke):
        return Stroke(stroke.vectors, stroke.strength, stroke.pressure, stroke.uv_rotation,
        stroke.line_width, stroke.draw_cyclic, stroke.start_cap_mode, stroke.end_cap_mode,
        stroke.material_index, stroke.display_mode, stroke.frame_number)
