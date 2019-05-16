import bpy
from ... base_types import AnimationNode, VectorizedSocket

class GPencilStrokeEndCapNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_GPencilStrokeEndCapNode"
    bl_label = "GPencil Stroke End Cap"
    bl_width_default = 165

    useStrokeList: VectorizedSocket.newProperty()
    useEndBooleanList: VectorizedSocket.newProperty()

    def create(self):
        self.newInput(VectorizedSocket("Stroke", "useStrokeList",
            ("Stroke", "stroke"), ("Strokes", "strokes")))
        self.newInput(VectorizedSocket("Boolean", "useEndBooleanList",
            ("End Cap (ROUND/FLAT)", "endCap"), ("End Caps (ROUND/FLAT)", "endCaps")))
        self.newOutput(VectorizedSocket("Stroke", "useStrokeList",
            ("Stroke", "stroke"), ("Strokes", "strokes")))

    def getExecutionFunctionName(self):
        if self.useStrokeList and self.useEndBooleanList:
            return "executeListEndCapList"    
        elif self.useStrokeList:
            return "executeList"
        else:
            return "executeSingle"

    def executeSingle(self, stroke, endCap):
        if stroke is None: return None
        self.strokeEndCap(stroke, endCap)
        return stroke

    def executeList(self, strokes, endCap):
        if len(strokes) == 0: return strokes
        for stroke in strokes:
            if stroke is not None:
                self.strokeEndCap(stroke, endCap)
        return strokes

    def executeListEndCapList(self, strokes, endCaps):
        if len(strokes) == 0 or len(endCaps) == 0 or len(strokes) != len(endCaps): return strokes
        for i, stroke in enumerate(strokes):
            if stroke is not None: self.strokeEndCap(stroke, endCaps[i])
        return strokes
    
    def strokeEndCap(self, stroke, endCap):
        if endCap:
            stroke.end_cap_mode = 'FLAT'
        else:
            stroke.end_cap_mode = 'ROUND'
        return stroke