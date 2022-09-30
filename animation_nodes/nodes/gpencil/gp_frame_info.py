import bpy
from bpy.props import *
from ... events import propertyChanged
from ... data_structures import GPStroke
from ... base_types import AnimationNode, VectorizedSocket

strokeTypeItems = [
    ("ALL", "All Strokes", "Get all strokes", "NONE", 0),
    ("INDEX", "Index Stroke ", "Get a specific stroke", "NONE", 1)
]

class GPFrameInfoNode(AnimationNode, bpy.types.Node):
    bl_idname = "an_GPFrameInfoNode"
    bl_label = "GP Frame Info"
    errorHandlingType = "EXCEPTION"

    strokeType: EnumProperty(name = "Stroke Type", default = "ALL",
        items = strokeTypeItems, update = AnimationNode.refresh)

    useIntegerList: VectorizedSocket.newProperty()

    def create(self):
        self.newInput("GPFrame", "Frame", "frame", dataIsModified = True)

        if self.strokeType == "ALL":
            self.newOutput("GPStroke List", "Strokes", "strokes")
        elif self.strokeType == "INDEX":
            self.newInput(VectorizedSocket("Integer", "useIntegerList",
            ("Stroke Index", "strokeIndex"), ("Stroke Indices", "strokeIndices")))

            self.newOutput(VectorizedSocket("GPStroke", "useIntegerList",
            ("Stroke", "stroke"), ("Strokes", "strokes")))
        self.newOutput("Integer", "Frame Number", "frameNumber")

    def draw(self, layout):
        layout.prop(self, "strokeType", text = "")

    def getExecutionFunctionName(self):
        if self.strokeType == "ALL":
            return "execute_AllStrokes"
        elif self.strokeType == "INDEX":
            if self.useIntegerList:
                return "execute_StrokeIndices"
            else:
                return "execute_StrokeIndex"

    def execute_AllStrokes(self, frame):
        return frame.strokes, frame.frameNumber

    def execute_StrokeIndex(self, frame, strokeIndex):
        strokes = frame.strokes
        if len(strokes) == 0:
            return GPStroke(), frame.frameNumber
        return self.getStroke(strokes, strokeIndex), frame.frameNumber

    def execute_StrokeIndices(self, frame, strokeIndices):
        strokes = frame.strokes
        if len(strokes) == 0:
            return [], frame.frameNumber

        outStrokes = [self.getStroke(strokes, index) for index in strokeIndices]
        return outStrokes, frame.frameNumber

    def getStroke(self, strokes, strokeIndex):
        if strokeIndex < 0 or strokeIndex >= len(strokes):
            self.raiseErrorMessage(f"There is no stroke for index '{strokeIndex}'.")
        return strokes[strokeIndex]
