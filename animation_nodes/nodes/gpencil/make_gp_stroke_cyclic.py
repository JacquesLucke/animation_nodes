import bpy
from ... base_types import AnimationNode, VectorizedSocket
from ... data_structures import VirtualBooleanList, VirtualPyList, GPStroke

class MakeGPStrokeCyclicNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_MakeGPStrokeCyclicNode"
    bl_label = "Make GP Stroke Cyclic"

    useStrokeList: VectorizedSocket.newProperty()
    useBooleanList: VectorizedSocket.newProperty()

    def create(self):
        self.newInput(VectorizedSocket("GPStroke", "useStrokeList",
            ("Stroke", "stroke"), ("Strokes", "strokes")), dataIsModified = True)
        self.newInput(VectorizedSocket("Boolean", "useBooleanList",
            ("Cyclic", "cyclic"), ("Cyclics", "cyclics")))
        self.newOutput(VectorizedSocket("GPStroke", ["useStrokeList", "useBooleanList"],
            ("Stroke", "outStroke"), ("Strokes", "outStrokes")))

    def getExecutionFunctionName(self):
        if self.useStrokeList or self.useBooleanList:
            return "execute_StrokeList_CyclicList"
        else:
            return "execute_Stroke_Cyclic"

    def execute_Stroke_Cyclic(self, stroke, cyclic):
        stroke.drawCyclic = cyclic
        return stroke

    def execute_StrokeList_CyclicList(self, strokes, cyclics):
        _strokes = VirtualPyList.create(strokes, GPStroke())
        _cyclics = VirtualBooleanList.create(cyclics, False)
        amount = VirtualPyList.getMaxRealLength(_strokes, _cyclics)

        outStrokes = []
        for i in range(amount):
            strokeNew = _strokes[i].copy()
            strokeNew.drawCyclic = _cyclics[i]
            outStrokes.append(strokeNew)
        return outStrokes
