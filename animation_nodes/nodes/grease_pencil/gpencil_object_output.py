from itertools import chain
import bpy
from bpy.props import *
from ... base_types import AnimationNode, VectorizedSocket

strokeTypeItems = [
    ("STROKE", "Stroke", "One Stroke", "NONE", 0),
    ("STROKES", "Stroke List", "Stroke List", "NONE", 1) 
]

class GPencilObjectOutputNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_GPencilObjectOutputNode"
    bl_label = "GPencil Object Output"
    errorHandlingType = "MESSAGE"
    bl_width_default = 165

    useStrokeList: VectorizedSocket.newProperty()

    def create(self):
        socket = self.newInput("Object", "Object", "object")
        socket.defaultDrawType = "PROPERTY_ONLY"
        socket.objectCreationType = "GPENCIL"
        self.newInput(VectorizedSocket("Stroke", "useStrokeList",
            ("Stroke", "stroke"), ("Strokes", "strokes")))
        self.newInput("Integer", "GP-Layer Index", "gpLayerIndex", value = 0)
        self.newOutput("Object", "Object", "object")
        
    def getExecutionFunctionName(self):
        if self.useStrokeList:
            return "executeStrokeList"
        else:
            return "executeStroke"

    def executeStroke(self, object, stroke, gpLayerIndex):
        if self.isValidObject(object) is False or stroke is None: return object
        
        gpencil = object.data
        if gpencil is None: return object

        gpencilLayer = self.getLayer(gpencil, gpLayerIndex)
        if gpencilLayer is None: return object
        
        gpencilFrame = self.getFrame(gpencilLayer, 0, 1)
        if gpencilFrame is None:
            self.setErrorMessage("Current GPencil Frame has same the frame-number. Each GPencil Frame must have unique frame-number!")
            return object
        gpencilFrame = self.setFrameStrokes(gpencilFrame, [stroke])
        gpencilStroke = self.setStrokeProperties(self.getStroke(0, gpencilFrame), stroke)
        
        gpencilPoints = self.setStrokePoints(gpencilStroke, stroke)
        if gpencilPoints is not None:
            gpencilPoints.foreach_set('co', self.flatList(stroke.vectors))
            gpencilPoints.foreach_set('strength', stroke.strength)
            gpencilPoints.foreach_set('pressure', stroke.pressure)
            gpencilPoints.foreach_set('uv_rotation', stroke.uv_rotation)
        
        gpencilFrame.strokes.update()
        gpencil.layers.active.frames.update()
        return object

    def executeStrokeList(self, object, strokes, gpLayerIndex):
        if self.isValidObject(object) is False: return object
        gpencil = object.data
        if gpencil is None: return object

        gpencilLayer = self.getLayer(gpencil, gpLayerIndex)
        if gpencilLayer is None: return object
        
        gpencilFrame = self.getFrame(gpencilLayer, 0, 1)
        if gpencilFrame is None:
            self.setErrorMessage("Current GPencil Frame has same the frame-number. Each GPencil Frame must have unique frame-number!")
            return object
        gpencilFrame = self.setFrameStrokes(gpencilFrame, strokes)

        for i, stroke in enumerate(strokes):
            gpencilStroke = self.setStrokeProperties(self.getStroke(i, gpencilFrame), stroke)
            gpencilPoints = self.setStrokePoints(gpencilStroke, stroke)
            if gpencilPoints is not None:
                gpencilPoints.foreach_set('co', self.flatList(stroke.vectors))
                gpencilPoints.foreach_set('strength', stroke.strength)
                gpencilPoints.foreach_set('pressure', stroke.pressure)
                gpencilPoints.foreach_set('uv_rotation', stroke.uv_rotation)
        gpencilFrame.strokes.update()
        gpencil.layers.active.frames.update()
        return object

    def getLayer(self, gpencil, gpLayerIndex):
        if gpLayerIndex < 0: return None
        try:
            index = len(gpencil.layers) - gpLayerIndex - 1
            if index < 0: return gpencil.layers.new("ANGPencil_Layer", set_active = True)
            return gpencil.layers[index]
        except: return gpencil.layers.new("ANGPencil_Layer", set_active = True)

    def getFrame(self, gprencilLayer, gpFrameIndex, frameNumber):
        try: return gprencilLayer.frames[gpFrameIndex]
        except:
            try: return gprencilLayer.frames.new(frameNumber)
            except: return None

    def getStroke(self, index, gpFrame):
        try: return gpFrame.strokes[index]
        except: return gpFrame.strokes.new()

    def setFrameStrokes(self, gpencilFrame, strokes):
        lenStrokes = len(strokes)
        lenGStrokes = len(gpencilFrame.strokes)
        while lenStrokes < lenGStrokes:
            gpencilFrame.strokes.remove(gpencilFrame.strokes[lenGStrokes - 1])
            lenGStrokes = len(gpencilFrame.strokes)
        return gpencilFrame

    def setStrokePoints(self, gpencilStroke, stroke):
        lenSPoints = len(stroke.vectors)
        lenGPoints = len(gpencilStroke.points)
        if lenSPoints != 0 and lenSPoints > lenGPoints:
            gpencilStroke.points.add(lenSPoints - lenGPoints, strength = 0.75, pressure = 1)
        elif lenSPoints < lenGPoints:
            while lenSPoints < lenGPoints:
                gpencilStroke.points.pop()
                lenGPoints = len(gpencilStroke.points)
        return gpencilStroke.points

    def setStrokeProperties(self, gpencilStroke, stroke):
        gpencilStroke.line_width = stroke.line_width
        gpencilStroke.material_index = stroke.material_index
        gpencilStroke.display_mode = "3DSPACE"
        if stroke.draw_cyclic: gpencilStroke.draw_cyclic = True
        else: gpencilStroke.draw_cyclic = False
        
        if stroke.start_cap_mode == 'FLAT':
            gpencilStroke.start_cap_mode = 'FLAT'
        else:
            gpencilStroke.start_cap_mode = 'ROUND'

        if stroke.end_cap_mode == 'FLAT':
            gpencilStroke.end_cap_mode = 'FLAT'
        else:
            gpencilStroke.end_cap_mode = 'ROUND'
        return gpencilStroke

    def isValidObject(self, object):
        if object is None: return False
        if object.type != "GPENCIL" or object.mode != "OBJECT":
            self.setErrorMessage("Object is not in object mode or is no gpencil object")
            return False
        return True

    def flatList(self, vectors):
        return list(chain.from_iterable(vectors))