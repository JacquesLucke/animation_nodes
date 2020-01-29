import bpy
from bpy.props import *
from ... base_types import AnimationNode, VectorizedSocket

class GPencilObjectOutputNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_GPencilObjectOutputNode"
    bl_label = "GPencil Object Output"
    errorHandlingType = "EXCEPTION"

    useLayerList: VectorizedSocket.newProperty()

    def create(self):
        socket = self.newInput("Object", "Object", "object")
        socket.defaultDrawType = "PROPERTY_ONLY"
        socket.objectCreationType = "GPENCIL"
        self.newInput(VectorizedSocket("GPLayer", "useLayerList",
            ("Layer", "layer"), ("Layers", "layers")))
        self.newOutput("Object", "Object", "object")

    def getExecutionFunctionName(self):
        if self.useLayerList:
            return "execute_LayerList"
        else:
            return "execute_Layer"

    def execute_Layer(self, object, layer):
        if object is None: return None
        gpencil = self.getObjectData(object)

        if layer is None: return object
        gpencilLayer = self.getLayer(gpencil, layer)
        gpencilLayer.clear()
        gpFrameNumbers = self.getFrameNumbers(gpencilLayer, layer)
        gpFrames = gpencilLayer.frames

        for frame in layer.frames:
            index = self.getFrameNumberIndex(gpFrameNumbers, frame.frameNumber)
            gpFrame = gpFrames[index]
            gpFrame.clear()
            for stroke in frame.strokes:
                gpStroke = self.setStrokeProperties(gpFrame.strokes.new(), stroke)
                gpPoints = gpStroke.points
                vertices = stroke.vertices
                gpPoints.add(len(vertices), strength = 0.75, pressure = 1)
                gpPoints.foreach_set("co", vertices.asNumpyArray())
                gpPoints.foreach_set("strength", stroke.strength)
                gpPoints.foreach_set("pressure", stroke.pressure)
                gpPoints.foreach_set("uv_rotation", stroke.uv_rotation)
            gpFrame.strokes.update()
        gpencil.layers.active.frames.update()
        return object

    def execute_LayerList(self, object, layers):
        if object is None: None
        gpencil = self.getObjectData(object)

        if len(layers) == 0: return object
        for layer in layers:
            if layer is None: return
            gpencilLayer = self.getLayer(gpencil, layer)
            gpencilLayer.clear()
            gpFrameNumbers = self.getFrameNumbers(gpencilLayer, layer)
            gpFrames = gpencilLayer.frames

            for frame in layer.frames:
                index = self.getFrameNumberIndex(gpFrameNumbers, frame.frameNumber)
                gpFrame = gpFrames[index]
                gpFrame.clear()
                for stroke in frame.strokes:
                    gpStroke = self.setStrokeProperties(gpFrame.strokes.new(), stroke)
                    gpPoints = gpStroke.points
                    vertices = stroke.vertices
                    gpPoints.add(len(vertices), strength = 0.75, pressure = 1)
                    gpPoints.foreach_set("co", vertices.asNumpyArray())
                    gpPoints.foreach_set("strength", stroke.strength)
                    gpPoints.foreach_set("pressure", stroke.pressure)
                    gpPoints.foreach_set("uv_rotation", stroke.uv_rotation)
                gpFrame.strokes.update()
        gpencil.layers.active.frames.update()
        return object

    def getLayer(self, gpencil, layer):
        layerName = layer.layerName
        try: gpencilLayer = gpencil.layers[layerName]
        except: gpencilLayer = gpencil.layers.new(layerName, set_active=True)
        gpencilLayer.blend_mode = layer.blendMode
        gpencilLayer.opacity = layer.opacity
        gpencilLayer.pass_index = layer.passIndex
        return gpencilLayer

    def getFrameNumbers(self, gpencilLayer, layer):
        frameNumbers = layer.frameNumbers
        for frameNumber in frameNumbers:
            gpencilLayer.frames.new(frameNumber, active = True)
        return frameNumbers

    def getFrameNumberIndex(self, frameNumbers, frameNumber):
        return frameNumbers.index(frameNumber)

    def setStrokeProperties(self, gpencilStroke, stroke):
        gpencilStroke.line_width = stroke.line_width
        gpencilStroke.material_index = stroke.material_index
        gpencilStroke.display_mode = stroke.display_mode
        if stroke.draw_cyclic: gpencilStroke.draw_cyclic = True
        else: gpencilStroke.draw_cyclic = False

        if stroke.start_cap_mode == "FLAT":
            gpencilStroke.start_cap_mode = "FLAT"
        else:
            gpencilStroke.start_cap_mode = "ROUND"

        if stroke.end_cap_mode == "FLAT":
            gpencilStroke.end_cap_mode = "FLAT"
        else:
            gpencilStroke.end_cap_mode = "ROUND"
        return gpencilStroke

    def getObjectData(self, object):
        if object.type != "GPENCIL":
            self.raiseErrorMessage("Object is not a grease pencil object.")
        if object.mode != "OBJECT":
            self.raiseErrorMessage("Object is not in object mode.")
        return object.data
