import bpy
from bpy.props import *
from ... base_types import AnimationNode, VectorizedSocket

class GPencilStrokeCyclicNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_GPencilStrokeCyclicNode"
    bl_label = "GPencil Stroke Cyclic"

    useStrokeList: VectorizedSocket.newProperty()
    useBooleanList: VectorizedSocket.newProperty()

    def create(self):
        self.newInput(VectorizedSocket("Stroke", "useStrokeList",
            ("Stroke", "stroke"), ("Strokes", "strokes")))
        self.newInput(VectorizedSocket("Boolean", "useBooleanList",
            ("Cyclic", "cyclic"), ("Cyclics", "cyclics")))
        self.newOutput(VectorizedSocket("Stroke", "useStrokeList",
            ("Stroke", "stroke"), ("Strokes", "strokes")))
    
    def getExecutionFunctionName(self):
        if self.useStrokeList and self.useBooleanList:
            return "executeListList"
        elif self.useStrokeList:
            return "executeList"
        else:
            return "executeSingle"

    def executeSingle(self, stroke, cyclic):
        if stroke is None: return None
        stroke.draw_cyclic = cyclic
        return stroke

    def executeList(self, strokes, cyclic):
        if len(strokes) == 0: return strokes
        for stroke in strokes:
            if stroke is not None: stroke.draw_cyclic = cyclic
        return strokes

    def executeListList(self, strokes, cyclics):
        if len(strokes) == 0 or len(cyclics) == 0 or len(strokes) != len(cyclics): return strokes
        for i, stroke in enumerate(strokes):
            if stroke is not None: stroke.draw_cyclic = cyclics[i]
        return strokes
