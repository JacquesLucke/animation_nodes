import bpy
from bpy.props import *
from ... base_types import AnimationNode, VectorizedSocket

displayModeTypeItems = [
    ("SCREEN", "Screen", "", "NONE", 0),
    ("3DSPACE", "3D Space", "", "NONE", 1),
    ("2DSPACE", "2D Space", "", "NONE", 2),
    ("2DIMAGE", "2D Image", "", "NONE", 3)
]

class GPStrokeDisplayModeNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_GPStrokeDisplayModeNode"
    bl_label = "GP Stroke Display Mode"
    bl_width_default = 165

    displayModeType: EnumProperty(name = "Display Mode", default = "SCREEN",
        items = displayModeTypeItems, update = AnimationNode.refresh)

    useStrokeList: VectorizedSocket.newProperty()

    def create(self):
        self.newInput(VectorizedSocket("GPStroke", "useStrokeList",
            ("Stroke", "stroke"), ("Strokes", "strokes")), dataIsModified = True)
        self.newOutput(VectorizedSocket("GPStroke", "useStrokeList",
            ("Stroke", "outStroke"), ("Strokes", "outStrokes")))

    def draw(self, layout):
        layout.prop(self, "displayModeType", text = "")

    def getExecutionFunctionName(self):
        if self.useStrokeList:
            return "executeList"
        else:
            return "executeSingle"

    def executeSingle(self, stroke):
        if stroke is None: return None
        return self.strokeDisplayMode(stroke)

    def executeList(self, strokes):
        if len(strokes) == 0: return strokes
        for stroke in strokes:
            if stroke is not None:
                self.strokeDisplayMode(stroke)
        return strokes

    def strokeDisplayMode(self, stroke):
        if self.displayModeType == "SCREEN":
            stroke.displayMode = "SCREEN"
        elif self.displayModeType == "3DSPACE":
            stroke.displayMode = "3DSPACE"
        elif self.displayModeType == "2DSPACE":
            stroke.displayMode = "2DSPACE"
        elif self.displayModeType == "2DIMAGE":
            stroke.displayMode = "2DIMAGE"
        return stroke
