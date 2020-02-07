import bpy
from ... data_structures import VirtualBooleanList
from ... base_types import AnimationNode, VectorizedSocket

class GPSetStrokeCyclicNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_GPSetStrokeCyclicNode"
    bl_label = "GP Set Stroke Cyclic"

    useStrokeList: VectorizedSocket.newProperty()
    useBooleanList: VectorizedSocket.newProperty()

    def create(self):
        self.newInput(VectorizedSocket("GPStroke", "useStrokeList",
            ("Stroke", "stroke"), ("Strokes", "strokes")), dataIsModified = True)
        self.newInput(VectorizedSocket("Boolean", "useBooleanList",
            ("Cyclic", "cyclic"), ("Cyclics", "cyclics")))
        self.newOutput(VectorizedSocket("GPStroke", ["useStrokeList", "useBooleanList"],
            ("Stroke", "stroke"), ("Strokes", "strokes")))

    def getExecutionFunctionName(self):
        if self.useStrokeList and self.useBooleanList:
            return "execute_StrokeList_CyclicList"
        elif self.useStrokeList:
            return "execute_StrokeList_Cyclic"
        elif self.useBooleanList:
            return "execute_Stroke_CyclicList"
        else:
            return "execute_Stroke_Cyclic"

    def execute_Stroke_Cyclic(self, stroke, cyclic):
        stroke.drawCyclic = cyclic
        return stroke

    def execute_Stroke_CyclicList(self, stroke, cyclics):
        if len(cyclics) == 0: return [stroke]

        strokes = []
        for cyclic in cyclics:
            strokeNew = stroke.copy()
            strokeNew.drawCyclic = cyclic
            strokes.append(strokeNew)
        return strokes

    def execute_StrokeList_Cyclic(self, strokes, cyclic):
        if len(strokes) == 0: return strokes
        for stroke in strokes:
            stroke.drawCyclic = cyclic
        return strokes

    def execute_StrokeList_CyclicList(self, strokes, cyclics):
        if len(strokes) == 0 or len(cyclics) == 0: return strokes
        cyclics = VirtualBooleanList.create(cyclics, False)
        for i, stroke in enumerate(strokes):
            stroke.drawCyclic = cyclics[i]
        return strokes
