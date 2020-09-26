import bpy
from bpy.props import *
from ... events import propertyChanged
from ... utils.depsgraph import getEvaluatedID
from ... base_types import AnimationNode, VectorizedSocket
from ... data_structures import GPLayer, GPFrame, GPStroke, Color, FloatList, Vector3DList, ColorList

importTypeItems = [
    ("ALL", "All", "Get all grease pencil layers", "NONE", 0),
    ("SINGLE", "Single", "Get a specific grease pencil layer", "NONE", 1)
]

class GPObjectInputNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_GPObjectInputNode"
    bl_label = "GP Object Input"
    errorHandlingType = "EXCEPTION"

    importType: EnumProperty(name = "Import Type", default = "ALL",
        items = importTypeItems, update = AnimationNode.refresh)

    def create(self):
        self.newInput("Object", "Object", "object", defaultDrawType = "PROPERTY_ONLY")
        self.newInput("Boolean", "Use World Space", "useWorldSpace", value = True)

        if self.importType == "SINGLE":
            self.newInput("Text", "Layer Name", "layerName")
            self.newOutput("GPLayer", "Layer", "layer")
        elif self.importType == "ALL":
            self.newOutput("GPLayer List", "Layers", "layers")

    def drawAdvanced(self, layout):
        layout.prop(self, "importType")

    def getExecutionFunctionName(self):
        if self.importType == "SINGLE":
            return "executeSingle"
        elif self.importType == "ALL":
            return "executeList"

    def executeSingle(self, object, useWorldSpace, layerName):
        if object is None:
            return GPLayer()

        evaluatedObject = getEvaluatedID(object)
        layer = self.getLayer(evaluatedObject, layerName)
        return GPLayer(layer.info, self.getFrames(layer, evaluatedObject, useWorldSpace),
                       layer.blend_mode, layer.opacity, layer.use_lights, self.getTintColor(layer), layer.tint_factor,
                       layer.line_change, layer.pass_index, False, self.getMaskLayers(layer, object, useWorldSpace))

    def executeList(self, object, useWorldSpace):
        if object is None:
            return []

        evaluatedObject = getEvaluatedID(object)
        gpencilLayers = []
        for layer in self.getLayers(evaluatedObject):
            gpencilLayers.append(GPLayer(layer.info, self.getFrames(layer, evaluatedObject, useWorldSpace),
                                         layer.blend_mode, layer.opacity, layer.use_lights, self.getTintColor(layer), layer.tint_factor,
                                         layer.line_change, layer.pass_index, False, self.getMaskLayers(layer, object, useWorldSpace)))
        return gpencilLayers

    def getLayer(self, object, layerName):
        layers = self.getLayers(object)
        if layerName in layers:
            return layers[layerName]
        else:
            self.raiseErrorMessage(f"Object doesn't have a layer with the name '{layerName}'.")

    def getLayers(self, object):
        gpencil = self.getObjectData(object)
        return gpencil.layers

    def getTintColor(self, layer):
        color = layer.tint_color
        return Color((color.r, color.g, color.b, 1))

    def getMaskLayers(self, layer, object, useWorldSpace):
        maskLayers = []
        for maskLayer in layer.mask_layers:
            gpMaskLayer = self.executeSingle(object, useWorldSpace, maskLayer.name)
            gpMaskLayer.invertAsMask = maskLayer.invert
            maskLayers.append(gpMaskLayer)
        return maskLayers

    def getObjectData(self, object):
        if object.type != "GPENCIL":
            self.raiseErrorMessage("Object is not a grease pencil object.")
        if object.mode == "EDIT":
            self.raiseErrorMessage("Object is not in object mode.")
        return object.data

    def getFrames(self, layer, object, useWorldSpace):
        frames = [GPFrame(self.getStrokes(frame.strokes, object, useWorldSpace), frame.frame_number)
                  for frame in layer.frames]
        return frames

    def getStrokes(self, strokes, object, useWorldSpace):
        newStrokes = [self.getStroke(stroke, object, useWorldSpace) for stroke in strokes]
        return newStrokes

    def getStroke(self, stroke, object, useWorldSpace):
        strokePoints = stroke.points
        amount = len(strokePoints)

        vertices = Vector3DList(length = amount)
        strengths = FloatList(length = amount)
        pressures = FloatList(length = amount)
        uvRotations = FloatList(length = amount)
        vertexColors = ColorList(length = amount)

        strokePoints.foreach_get("co", vertices.asNumpyArray())
        if useWorldSpace: vertices.transform(object.matrix_world)

        strokePoints.foreach_get("strength", strengths.asNumpyArray())
        strokePoints.foreach_get("pressure", pressures.asNumpyArray())
        strokePoints.foreach_get("uv_rotation", uvRotations.asNumpyArray())
        strokePoints.foreach_get("vertex_color", vertexColors.asNumpyArray())

        return GPStroke(vertices, strengths, pressures, uvRotations, vertexColors, stroke.line_width, stroke.hardness,
                        stroke.draw_cyclic, stroke.start_cap_mode, stroke.end_cap_mode, self.getVertexColorFill(stroke),
                        stroke.material_index, stroke.display_mode)

    def getVertexColorFill(self, stroke):
        color = stroke.vertex_color_fill
        return Color(tuple(color))
