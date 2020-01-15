import bpy
from ... base_types import AnimationNode, VectorizedSocket

class GPencilStrokeStartCapNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_GPencilStrokeStartCapNode"
    bl_label = "GPencil Stroke Start Cap"
    bl_width_default = 165

    useStrokeList: VectorizedSocket.newProperty()
    useStartBooleanList: VectorizedSocket.newProperty()

    def create(self):
        self.newInput(VectorizedSocket("Stroke", "useStrokeList",
            ("Stroke", "stroke"), ("Strokes", "strokes")), dataIsModified = True)
        self.newInput(VectorizedSocket("Boolean", "useStartBooleanList",
            ("Start Cap (ROUND/FLAT)", "startCap"), ("Start Caps (ROUND/FLAT)", "startCaps")))
        self.newOutput(VectorizedSocket("Stroke", "useStrokeList",
            ("Stroke", "stroke"), ("Strokes", "strokes")), dataIsModified = True)

    def getExecutionFunctionName(self):
        if self.useStrokeList and self.useStartBooleanList:
            return "executeListStartCapList"
        elif self.useStrokeList:
            return "executeList"
        else:
            return "executeSingle"

    def executeSingle(self, stroke, startCap):
        if stroke is None: return None
        self.strokeStartCap(stroke, startCap)
        return stroke 

    def executeList(self, strokes, startCap):
        if len(strokes) == 0: return strokes
        for stroke in strokes:
            if stroke is not None:
                self.strokeStartCap(stroke, startCap)
        return strokes

    def executeListStartCapList(self, strokes, startCaps):
        if len(strokes) == 0 or len(startCaps) == 0 or len(strokes) != len(startCaps): return strokes
        for i, stroke in enumerate(strokes):
            if stroke is not None: self.strokeStartCap(stroke, startCaps[i])
        return strokes

    def strokeStartCap(self, stroke, startCap):
        if startCap:
            stroke.start_cap_mode = 'FLAT'
        else:
            stroke.start_cap_mode = 'ROUND'
        return stroke