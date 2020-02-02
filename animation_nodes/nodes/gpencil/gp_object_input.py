import bpy
from bpy.props import *
from ... events import propertyChanged
from ... utils.depsgraph import getEvaluatedID
from ... base_types import AnimationNode, VectorizedSocket
from ... data_structures import GPLayer, GPFrame, GPStroke, DoubleList, Vector3DList

layerTypeItems = [
    ("ALL", "All", "Get all grease pencil layers", "NONE", 0),
    ("SINGLE", "Single", "Get a specific grease pencil layer", "NONE", 1)
]

class GPObjectInputNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_GPObjectInputNode"
    bl_label = "GP Object Input"
    errorHandlingType = "EXCEPTION"

    layerType: EnumProperty(name = "Layer Type", default = "SINGLE",
        items = layerTypeItems, update = AnimationNode.refresh)

    def create(self):
        self.newInput("Object", "Object", "object", defaultDrawType = "PROPERTY_ONLY")
        self.newInput("Boolean", "Use World Space", "useWorldSpace", value = True)

        if self.layerType == "SINGLE":
            self.newInput("Text", "Layer Name", "layerName")
            self.newOutput("GPLayer", "Layer", "layer")
        elif self.layerType == "ALL":
            self.newOutput("GPLayer List", "Layers", "layers")

    def draw(self, layout):
        layout.prop(self, "layerType", text = "")

    def getExecutionFunctionName(self):
        if self.layerType == "SINGLE":
            return "executeSingle"
        elif self.layerType == "ALL":
            return "executeList"

    def executeSingle(self, object, useWorldSpace, layerName):
        if object is None:
            return GPLayer()

        evaluatedObject = getEvaluatedID(object)
        if useWorldSpace:
            worldMatrix = evaluatedObject.matrix_world
        else:
            worldMatrix = None

        layer = self.getLayer(evaluatedObject, layerName)
        return GPLayer(layer.info, self.getFrames(layer, worldMatrix), layer.blend_mode, layer.opacity,
                       layer.pass_index)

    def executeList(self, object, useWorldSpace):
        if object is None:
            return []

        evaluatedObject = getEvaluatedID(object)
        if useWorldSpace:
            worldMatrix = evaluatedObject.matrix_world
        else:
            worldMatrix = None

        gpencilLayers = []
        for layer in self.getLayers(evaluatedObject):
            gpencilLayers.append(GPLayer(layer.info, self.getFrames(layer, worldMatrix), layer.blend_mode,
                                         layer.opacity, layer.pass_index))
        return gpencilLayers

    def getLayer(self, object, layerName):
        if object.type != "GPENCIL":
            self.raiseErrorMessage("Object is not a grease pencil object.")
        if object.mode == "EDIT":
            self.raiseErrorMessage("Object is not in object mode.")
        if layerName in object.data.layers:
            return object.data.layers[layerName]
        else:
            self.raiseErrorMessage(f"Object doesn't have a layer with the name '{layerName}'.")

    def getLayers(self, object):
        return object.data.layers

    def getFrames(self, layer, matrixWorld):
        frames = [GPFrame(self.getStrokes(frame.strokes, matrixWorld), frame.frame_number) for frame in layer.frames]
        return frames

    def getStrokes(self, strokes, matrixWorld):
        newStrokes = [self.getStroke(stroke, matrixWorld) for stroke in strokes]
        return newStrokes

    def getStroke(self, stroke, matrixWorld):
        strokePoints = stroke.points
        amount = len(strokePoints)

        vertices = Vector3DList(length = amount)
        strengths = DoubleList(length = amount)
        pressures = DoubleList(length = amount)
        uvRotations = DoubleList(length = amount)

        strokePoints.foreach_get("co", vertices.asNumpyArray())
        if matrixWorld is not None: vertices.transform(matrixWorld)

        strokePoints.foreach_get("strength", strengths.asNumpyArray())
        strokePoints.foreach_get("pressure", pressures.asNumpyArray())
        strokePoints.foreach_get("uv_rotation", uvRotations.asNumpyArray())

        return GPStroke(vertices, strengths, pressures, uvRotations, stroke.line_width, stroke.draw_cyclic,
                        stroke.start_cap_mode, stroke.end_cap_mode, stroke.material_index, stroke.display_mode)
