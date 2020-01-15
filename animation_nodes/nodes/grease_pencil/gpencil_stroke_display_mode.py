import bpy
from bpy.props import *
from ... base_types import AnimationNode, VectorizedSocket

displayModeTypeItems = [
    ("SCREEN", "Screen", "", "NONE", 0),
    ("3DSPACE", "3D Space", "", "NONE", 1),
    ("2DSPACE", "2D Space", "", "NONE", 2),
    ("2DIMAGE", "2D Image", "", "NONE", 3)    
]

class GPencilStrokeDisplayModeNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_GPencilStrokeDisplayModeNode"
    bl_label = "GPencil Stroke Display Mode"
    bl_width_default = 165

    displayModeType: EnumProperty(name = "Display Mode", default = "SCREEN",
        items = displayModeTypeItems, update = AnimationNode.refresh)
    
    useStrokeList: VectorizedSocket.newProperty()

    def create(self):
        self.newInput(VectorizedSocket("Stroke", "useStrokeList",
            ("Stroke", "stroke"), ("Strokes", "strokes")), dataIsModified = True)
        self.newOutput(VectorizedSocket("Stroke", "useStrokeList",
            ("Stroke", "outStroke"), ("Strokes", "outStrokes")), dataIsModified = True)

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

    def strokeDisplayMode(self, outStroke):
        if self.displayModeType == "SCREEN":
            outStroke.display_mode = 'SCREEN'
        elif self.displayModeType == "3DSPACE":
            outStroke.display_mode = '3DSPACE'
        elif self.displayModeType == "2DSPACE":
            outStroke.display_mode = '2DSPACE'
        elif self.displayModeType == "2DIMAGE":
            outStroke.display_mode = '2DIMAGE' 
        return outStroke