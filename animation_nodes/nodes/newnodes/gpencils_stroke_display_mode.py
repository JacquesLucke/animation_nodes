import bpy
from bpy.props import *
from ... data_structures import Stroke
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
            ("Stroke", "stroke"), ("Strokes", "strokes")))
        self.newOutput(VectorizedSocket("Stroke", "useStrokeList",
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
        outStroke = self.copyStroke(stroke)
        return self.strokeDisplayMode(outStroke)

    def executeList(self, strokes):
        if len(strokes) == 0: return strokes
        outStrokes = []
        for stroke in strokes:
            if stroke is not None:
                outStroke = self.copyStroke(stroke)
                self.strokeDisplayMode(outStroke)
                outStrokes.append(outStroke)
        return outStrokes

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

    def copyStroke(self, stroke):
        return Stroke(stroke.vectors, stroke.strength, stroke.pressure, stroke.uv_rotation,
        stroke.line_width, stroke.draw_cyclic, stroke.start_cap_mode, stroke.end_cap_mode,
        stroke.material_index, stroke.display_mode, stroke.frame_number)