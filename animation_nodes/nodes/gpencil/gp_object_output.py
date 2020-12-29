import bpy
from bpy.props import *
from ... base_types import AnimationNode, VectorizedSocket

class GPObjectOutputNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_GPObjectOutputNode"
    bl_label = "GP Object Output"
    errorHandlingType = "EXCEPTION"

    appendLayers: BoolProperty(name = "Append Layers", default = False,
        description = "This option allow to add custom layers",
        update = AnimationNode.refresh)

    useLayerList: VectorizedSocket.newProperty()

    def create(self):
        socket = self.newInput("Object", "Object", "object")
        socket.defaultDrawType = "PROPERTY_ONLY"
        socket.objectCreationType = "GPENCIL"
        self.newInput(VectorizedSocket("GPLayer", "useLayerList",
            ("Layer", "layer"), ("Layers", "layers")))
        self.newOutput("Object", "Object", "object")

    def drawAdvanced(self, layout):
        row = layout.row(align = True)
        row.prop(self, "appendLayers")

    def getExecutionFunctionName(self):
        if self.useLayerList:
            return "execute_LayerList"
        else:
            return "execute_Layer"

    def execute_Layer(self, object, layer):
        if object is None: return None
        if layer.layerName == "": return object

        gpencil = self.getObjectData(object)
        self.setLayerData(gpencil, layer)

        self.setMaskLayers(gpencil, layer)
        gpencil.layers.active.frames.update()
        return object

    def execute_LayerList(self, object, layers):
        if object is None: return None
        if len(layers) == 0: return object

        gpencil = self.getObjectData(object)
        for layer in layers:
            self.setLayerData(gpencil, layer)

        for layer in layers:
            self.setMaskLayers(gpencil, layer)
        gpencil.layers.active.frames.update()
        return object

    def setLayerData(self, gpencil, layer):
        gpencilLayer = self.getLayer(gpencil, layer)

        for frame in layer.frames:
            gpFrame = gpencilLayer.frames.new(frame.frameNumber, active = True)
            for stroke in frame.strokes:
                vertices = stroke.vertices
                if len(vertices) > 0:
                    gpStroke = gpFrame.strokes.new()
                    self.setStrokeProperties(gpStroke, stroke)
                    gpPoints = gpStroke.points
                    gpPoints.add(len(vertices), strength = 0.75, pressure = 1)
                    gpPoints.foreach_set("co", vertices.asNumpyArray())
                    gpPoints.foreach_set("strength", stroke.strengths)
                    gpPoints.foreach_set("pressure", stroke.pressures)
                    gpPoints.foreach_set("uv_rotation", stroke.uvRotations)
                    gpPoints.foreach_set("vertex_color", stroke.vertexColors.asNumpyArray())
            gpFrame.strokes.update()

    def setMaskLayers(self, gpencil, layer):
        gpLayers = gpencil.layers
        layerName = layer.layerName
        gpencilLayer = gpLayers[layer.layerName]
        for maskLayer in layer.maskLayers:
            maskLayerName = maskLayer.layerName
            if maskLayerName in gpLayers and maskLayerName != layerName and maskLayerName != "":
                gpencilLayer.mask_layers.add(gpLayers[maskLayerName])
                gpencilLayer.mask_layers[maskLayerName].invert = maskLayer.invertAsMask

    def setStrokeProperties(self, gpStroke, stroke):
        gpStroke.line_width = stroke.lineWidth
        gpStroke.hardness = stroke.hardness
        gpStroke.use_cyclic = stroke.useCyclic
        gpStroke.start_cap_mode = stroke.startCapMode
        gpStroke.end_cap_mode = stroke.endCapMode
        gpStroke.vertex_color_fill = stroke.vertexColorFill
        gpStroke.material_index = stroke.materialIndex
        gpStroke.display_mode = stroke.displayMode

    def getLayer(self, gpencil, layer):
        layerName = layer.layerName
        gpLayers = gpencil.layers
        if layerName in gpLayers and self.appendLayers:
            gpencilLayer = gpLayers[layerName]
            gpencilLayer.clear()
        else:
            gpencilLayer = gpLayers.new(layerName, set_active = True)
        gpencilLayer.blend_mode = layer.blendMode
        gpencilLayer.opacity = layer.opacity
        gpencilLayer.use_lights = layer.useLights
        gpencilLayer.tint_color = layer.tintColor[:3]
        gpencilLayer.tint_factor = layer.tintFactor
        gpencilLayer.line_change = layer.lineChange
        gpencilLayer.pass_index = layer.passIndex
        if len(layer.maskLayers) > 0:
            gpencilLayer.use_mask_layer = True
        return gpencilLayer

    def getObjectData(self, object):
        if object.type != "GPENCIL":
            self.raiseErrorMessage("Object is not a grease pencil object.")
        if object.mode == "EDIT":
            self.raiseErrorMessage("Object is not in object mode.")
        gpencil = object.data
        if not self.appendLayers: gpencil.clear()
        return gpencil
