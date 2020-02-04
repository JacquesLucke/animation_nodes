import bpy
from ... data_structures import VirtualBooleanList
from ... base_types import AnimationNode, VectorizedSocket

class GPStrokeCyclicNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_GPStrokeCyclicNode"
    bl_label = "GP Stroke Cyclic"

    useStrokeList: VectorizedSocket.newProperty()
    useBooleanList: VectorizedSocket.newProperty()

    def create(self):
        self.newInput(VectorizedSocket("GPStroke", "useStrokeList",
            ("Stroke", "stroke"), ("Strokes", "strokes")), dataIsModified = True)
        self.newInput(VectorizedSocket("Boolean", ["useStrokeList", "useBooleanList"],
            ("Cyclic", "cyclic"), ("Cyclics", "cyclics")))
        self.newOutput(VectorizedSocket("GPStroke", "useStrokeList",
            ("Stroke", "stroke"), ("Strokes", "strokes")))

    def getExecutionFunctionName(self):
        if self.useStrokeList and self.useBooleanList:
            return "executeListList"
        elif self.useStrokeList:
            return "executeList"
        else:
            return "executeSingle"

    def executeSingle(self, stroke, cyclic):
        stroke.drawCyclic = cyclic
        return stroke

    def executeList(self, strokes, cyclic):
        if len(strokes) == 0: return strokes
        for stroke in strokes:
            stroke.drawCyclic = cyclic
        return strokes

    def executeListList(self, strokes, cyclics):
        if len(strokes) == 0 or len(cyclics) == 0: return strokes
        cyclics = VirtualBooleanList.create(cyclics, False)
        for i, stroke in enumerate(strokes):
            stroke.drawCyclic = cyclics[i]
        return strokes
