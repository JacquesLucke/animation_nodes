from itertools import chain
import bpy
from bpy.props import *
from . c_utils import combineVectorList
from ... data_structures import DoubleList, VirtualDoubleList
from ... base_types import AnimationNode

strokeTypeItems = [
    ("STROKE", "Stroke", "One Stroke", "NONE", 0),
    ("STROKES", "Stroke List", "Stroke List", "NONE", 1) 
]

class GPencilObjectOutputNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_GPencilObjectOutputNode"
    bl_label = "GPencil Object Output"
    errorHandlingType = "MESSAGE"
    bl_width_default = 165

    strokeType: EnumProperty(name = "Stroke / Stroke list", default = "STROKE",
        items = strokeTypeItems, update = AnimationNode.refresh)

    def draw(self, layout):
        layout.prop(self, "strokeType", text = "")

    def create(self):
        self.newInput("Object", "Object", "object", defaultDrawType = "PROPERTY_ONLY")
        if self.strokeType == "STROKE":
            self.newInput("Stroke", "Stroke", "stroke")
        elif self.strokeType == "STROKES":
            self.newInput("Stroke List", "Strokes", "strokes")
        self.newOutput("Object", "Object", "object")
        
    def getExecutionFunctionName(self):
        if self.strokeType == "STROKE":
            return "executeStroke"
        elif self.strokeType == "STROKES":
            return "executeStrokeList"

    def executeStroke(self, object, stroke):
        if self.isValidObject(object) is False: return object
        gpencil = object.data
        gpencilFrame = self.getFrame(gpencil)
        if gpencilFrame is None:
            self.setErrorMessage("Grease Pencil Object should have at least a stroke frame!")
            return object
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

    def executeStrokeList(self, object, strokes):
        if self.isValidObject(object) is False: return object
        gpencil = object.data
        gpencilFrame = self.getFrame(gpencil)
        if gpencilFrame is None:
            self.setErrorMessage("Grease Pencil Object should have at least a stroke frame!")
            return object
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

    def getFrame(self, gpencil):
        return self.copyFrame(gpencil)

    def copyFrame(self, gpencil):
        try: return gpencil.layers.active.frames[0]
        except: return None

    def getStroke(self, index, gpFrame):
        try: return gpFrame.strokes[index]
        except: return gpFrame.strokes.new()

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

    def createVectorList(self, x, y, z):
        x, y, z = VirtualDoubleList.createMultiple((x, 0), (y, 0), (z, 0))
        amount = VirtualDoubleList.getMaxRealLength(x, y, z)
        return combineVectorList(amount, x, y, z)

    def flatList(self, vectors):
        return list(chain.from_iterable(vectors))