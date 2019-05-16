import bpy
from bpy.props import *
from ... events import propertyChanged
from ... data_structures import Stroke
from ... base_types import AnimationNode, VectorizedSocket

class GPencilStrokeMaterialIndexNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_GPencilStrokeMaterialIndexNode"
    bl_label = "GPencil Stroke Material Index"
    bl_width_default = 165

    useStrokeList: VectorizedSocket.newProperty()
    useIntegerList: VectorizedSocket.newProperty()

    def create(self):
        self.newInput(VectorizedSocket("Stroke", "useStrokeList",
            ("Stroke", "stroke"), ("Strokes", "strokes")))
        self.newInput(VectorizedSocket("Integer", "useIntegerList",
            ("Material Index", "materialIndex"), ("Material Indices", "materialIndices")))
        self.newOutput(VectorizedSocket("Stroke", "useStrokeList",
            ("Stroke", "outStroke"), ("Strokes", "outStrokes")))
    
    def getExecutionFunctionName(self):
        if self.useStrokeList and self.useIntegerList:
            return "executeListList"
        elif self.useStrokeList:
            return "executeList"
        else:
            return "executeSingle"

    def executeSingle(self, stroke, materialIndex):
        if stroke is None: return None
        outStroke = self.copyStroke(stroke)
        outStroke.material_index = materialIndex
        return outStroke

    def executeList(self, strokes, materialIndex):
        if len(strokes) == 0: return strokes
        outStrokes = []
        for stroke in strokes:
            if stroke is not None:
                outStroke = self.copyStroke(stroke)
                outStroke.material_index = materialIndex
                outStrokes.append(outStroke)
        return outStrokes

    def executeListList(self, strokes, materialIndices):
        if len(strokes) == 0 or len(materialIndices) == 0 or len(strokes) != len(materialIndices): return strokes
        outStrokes = []
        for i, stroke in enumerate(strokes):
            if stroke is not None:
                outStroke = self.copyStroke(stroke)
                outStroke.material_index = materialIndices[i]
                outStrokes.append(outStroke)
        return outStrokes

    def copyStroke(self, stroke):
        return Stroke(stroke.vectors, stroke.strength, stroke.pressure, stroke.uv_rotation,
        stroke.line_width, stroke.draw_cyclic, stroke.start_cap_mode, stroke.end_cap_mode,
        stroke.material_index, stroke.display_mode, stroke.frame_number)