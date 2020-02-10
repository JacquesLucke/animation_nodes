import bpy
from ... base_types import AnimationNode, VectorizedSocket
from ... data_structures import VirtualDoubleList, VirtualPyList, GPStroke

class SetGPStrokeLineWidthNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_SetGPStrokeLineWidthNode"
    bl_label = "Set GP Stroke Line Width"

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
        if self.useStrokeList or self.useFloatList:
            return "execute_StrokeList_LineWidthList"
        else:
            return "execute_Stroke_LineWidth"

    def execute_Stroke_LineWidth(self, stroke, lineWidth):
        stroke.lineWidth = lineWidth
        return stroke

    def execute_StrokeList_LineWidthList(self, strokes, lineWidths):
        _strokes = VirtualPyList.create(strokes, GPStroke())
        _lineWidths = VirtualDoubleList.create(lineWidths, 0)
        amount = VirtualPyList.getMaxRealLength(_strokes, _lineWidths)

        outStrokes = []
        for i in range(amount):
            strokeNew = _strokes[i].copy()
            strokeNew.lineWidth = _lineWidths[i]
            outStrokes.append(strokeNew)
        return outStrokes
