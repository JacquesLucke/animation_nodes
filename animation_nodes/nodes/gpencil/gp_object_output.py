import bpy
from bpy.props import *
from ... base_types import AnimationNode, VectorizedSocket

class GPObjectOutputNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_GPObjectOutputNode"
    bl_label = "GP Object Output"
    errorHandlingType = "EXCEPTION"

    appendCustomLayers: BoolProperty(name = "Append Custom Layers", default = False,
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
        row.prop(self, "appendCustomLayers")

    def getExecutionFunctionName(self):
        if self.useLayerList:
            return "execute_LayerList"
        else:
            return "execute_Layer"

    def execute_Layer(self, object, layer):
        if object is None: return None
        gpencil = self.getObjectData(object)

        if layer is None: return object
        self.setLayerData(gpencil, layer)
        gpencil.layers.active.frames.update()
        return object

    def execute_LayerList(self, object, layers):
        if object is None: return None
        gpencil = self.getObjectData(object)

        if len(layers) == 0: return object
        for layer in layers:
            self.setLayerData(gpencil, layer)
        gpencil.layers.active.frames.update()
        return object

    def setLayerData(self, gpencil, layer):
        gpencilLayer = self.getLayer(gpencil, layer)

        for frame in layer.frames:
            gpFrame = gpencilLayer.frames.new(frame.frameNumber, active = True)
            for stroke in frame.strokes:
                gpStroke = gpFrame.strokes.new()
                self.setStrokeProperties(gpStroke, stroke)
                gpPoints = gpStroke.points
                vertices = stroke.vertices
                gpPoints.add(len(vertices), strength = 0.75, pressure = 1)
                gpPoints.foreach_set("co", vertices.asNumpyArray())
                gpPoints.foreach_set("strength", stroke.strengths)
                gpPoints.foreach_set("pressure", stroke.pressures)
                gpPoints.foreach_set("uv_rotation", stroke.uvRotations)
            gpFrame.strokes.update()

    def setStrokeProperties(self, gpStroke, stroke):
        gpStroke.line_width = stroke.lineWidth
        gpStroke.material_index = stroke.materialIndex
        gpStroke.display_mode = stroke.displayMode
        gpStroke.draw_cyclic = stroke.drawCyclic
        gpStroke.start_cap_mode = stroke.startCapMode
        gpStroke.end_cap_mode = stroke.endCapMode

    def getLayer(self, gpencil, layer):
        layerName = layer.layerName
        if layerName in gpencil.layers:
            gpencilLayer = gpencil.layers[layerName]
            gpencilLayer.clear()
        else:
            gpencilLayer = gpencil.layers.new(layerName, set_active = True)
        gpencilLayer.blend_mode = layer.blendMode
        gpencilLayer.opacity = layer.opacity
        gpencilLayer.pass_index = layer.passIndex
        return gpencilLayer

    def getObjectData(self, object):
        if object.type != "GPENCIL":
            self.raiseErrorMessage("Object is not a grease pencil object.")
        if object.mode == "EDIT":
            self.raiseErrorMessage("Object is not in object mode.")
        gpencil = object.data
        if not self.appendCustomLayers: gpencil.clear()
        return gpencil
