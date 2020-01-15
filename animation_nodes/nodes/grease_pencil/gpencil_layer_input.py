import bpy
from bpy.props import *
from ... events import propertyChanged
from ... data_structures import Stroke
from ... base_types import AnimationNode
from .. vector.c_utils import combineVectorList
from ... data_structures import DoubleList, VirtualDoubleList

gframeTypeItems = [
    ("ACTIVE", "Active GFrame", "Active GFrame strokes", "NONE", 0),
    ("INDEX", "Index GFrame", "Specific GFrame strokes", "NONE", 1)
]

layerTypeItems = [
    ("ALL", "All Strokes", "Get all strokes data", "NONE", 0),
    ("INDEX", "Index Stroke ", "Get a specific strokes data", "NONE", 1)
]

class GPencilLayerInputNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_GPencilLayerInputNode"
    bl_label = "GPencil Layer Input"

    gframeType: EnumProperty(name = "GFrame Type", default = "ACTIVE",
        items = gframeTypeItems, update = AnimationNode.refresh)

    strokeType: EnumProperty(name = "Stroke Type", default = "ALL",
        items = layerTypeItems, update = AnimationNode.refresh)

    def create(self):
        self.newInput("Layer", "GPencil Layer", "gpencilLayer", dataIsModified = True)

        if self.gframeType == "INDEX":
            self.newInput("Integer", "GFrame Index", "gframeIndex")

        if self.strokeType == "INDEX":
            self.newInput("Integer", "Stroke Index", "strokeIndex")
            self.newOutput("Stroke", "Stroke", "stroke")
            self.newOutput("Integer", "Frame number", "frameNumber")
        elif self.strokeType == "ALL":
            self.newOutput("Stroke List", "Strokes", "strokes")
            self.newOutput("Integer", "Frame number", "frameNumber")

        visibleOutputs = ("Stroke", "Strokes")
        for socket in self.outputs:
            socket.hide = socket.name not in visibleOutputs

    def draw(self, layout):
        layout.prop(self, "gframeType", text = "")
        layout.prop(self, "strokeType", text = "")

    def getExecutionFunctionName(self):
        if self.gframeType == "INDEX":
            if self.strokeType == "INDEX":
                return "execute_IndexIndex"
            elif self.strokeType == "ALL":
                return "execute_AllIndex"

        elif self.gframeType == "ACTIVE":
            if self.strokeType == "INDEX":
                return "execute_IndexActive"
            elif self.strokeType == "ALL":
                return "execute_AllActive"

    def execute_IndexIndex(self, gpencilLayer, gframeIndex, strokeIndex):
        if gpencilLayer.layer is None: return None, None
        matrixWorld = gpencilLayer.matrix_world

        frame = self.getFrame(gpencilLayer, gframeIndex)
        if frame is None: return None, None
        frameNumber = frame.frame_number

        stroke = self.getStroke(frame, strokeIndex, matrixWorld)
        if stroke is None: return None, frameNumber
        return stroke, frameNumber

    def execute_AllIndex(self, gpencilLayer, gframeIndex):
        if gpencilLayer.layer is None: return [], None
        matrixWorld = gpencilLayer.matrix_world

        frame = self.getFrame(gpencilLayer, gframeIndex)
        if frame is None: return [], None
        frameNumber = frame.frame_number

        gpStrokes = frame.strokes
        strokes = []
        for gpStroke in gpStrokes:
            strokes.append(self.getStrokeData(gpStroke, matrixWorld))
        return strokes, frameNumber

    def execute_IndexActive(self, gpencilLayer, strokeIndex):
        if gpencilLayer.layer is None: return None, None
        matrixWorld = gpencilLayer.matrix_world

        frame = gpencilLayer.layer.active_frame
        if frame is None: return None, None
        frameNumber = frame.frame_number

        stroke = self.getStroke(frame, strokeIndex, matrixWorld)
        if stroke is None: return None, frameNumber
        return stroke, frameNumber

    def execute_AllActive(self, gpencilLayer):
        if gpencilLayer.layer is None: return [], None
        matrixWorld = gpencilLayer.matrix_world

        frame = gpencilLayer.layer.active_frame
        if frame is None: return [], None
        frameNumber = frame.frame_number

        gpStrokes = frame.strokes
        strokes = []
        for gpStroke in gpStrokes:
            strokes.append(self.getStrokeData(gpStroke, matrixWorld))
        return strokes, frameNumber

    def getFrame(self, gpencilLayer, gframeIndex):
        try: return gpencilLayer.layer.frames[gframeIndex]
        except: return None

    def getStroke(self, frame, strokeIndex, matrixWorld):
        try:
            gpStroke = frame.strokes[strokeIndex]
            return self.getStrokeData(gpStroke, matrixWorld)
        except: return None

    def getStrokeData(self, gpStroke, matrixWorld):
        xVectors = []
        yVectors = []
        zVectors = []

        gpStrokePoints = gpStroke.points
        totalPoints = len(gpStrokePoints)

        flatVectors = [0., 0., 0.]*totalPoints
        gpStrokePoints.foreach_get('co', flatVectors)
        xVectors = flatVectors[0::3]
        yVectors = flatVectors[1::3]
        zVectors = flatVectors[2::3]
        vectors = self.createVectorList(DoubleList.fromValues(xVectors), DoubleList.fromValues(yVectors), DoubleList.fromValues(zVectors))
        if matrixWorld is not None: vectors.transform(matrixWorld)

        strengths = [0.]*totalPoints
        gpStrokePoints.foreach_get('strength', strengths)
        pressures = [0.]*totalPoints
        gpStrokePoints.foreach_get('pressure', pressures)
        uvRotations = [0.]*totalPoints
        gpStrokePoints.foreach_get('uv_rotation', uvRotations)
        return Stroke(vectors, DoubleList.fromValues(strengths), DoubleList.fromValues(pressures), DoubleList.fromValues(uvRotations), gpStroke.line_width,
        gpStroke.draw_cyclic, gpStroke.start_cap_mode, gpStroke.end_cap_mode, gpStroke.material_index,
        gpStroke.display_mode)

    def createVectorList(self, x, y, z):
        x, y, z = VirtualDoubleList.createMultiple((x, 0), (y, 0), (z, 0))
        amount = VirtualDoubleList.getMaxRealLength(x, y, z)
        return combineVectorList(amount, x, y, z)
