import bpy
from bpy.props import *
from .. events import propertyChanged
from .. data_structures import BezierSpline, PolySpline
from .. base_types import AnimationNodeSocket, PythonListSocket
from .. data_structures.splines.from_blender import (createSplinesFromBlenderObject,
                                                     createSplineFromBlenderSpline)

class SplineSocket(bpy.types.NodeSocket, AnimationNodeSocket):
    bl_idname = "an_SplineSocket"
    bl_label = "Spline Socket"
    dataType = "Spline"
    drawColor = (0.8, 0.4, 1.0, 1.0)
    storable = True
    comparable = False

    object: PointerProperty(type = bpy.types.Object,
        description = "Use the first spline from this object",
        update = propertyChanged)

    useWorldSpace: BoolProperty(default = True,
        description = "Convert points to world space",
        update = propertyChanged)

    def drawProperty(self, layout, text, node):
        row = layout.row(align = True)
        row.prop(self, "object", text = text)
        self.invokeFunction(row, node, "handleEyedropperButton", icon = "EYEDROPPER", passEvent = True,
            description = "Assign active object to this socket (hold CTRL to open a rename object dialog)")
        if self.object:
            row.prop(self, "useWorldSpace", text = "", icon = "WORLD")

    def getValue(self):
        if getattr(self.object, "type", "") != "CURVE":
            return BezierSpline()

        bSplines = self.object.data.splines
        if len(bSplines) > 0:
            spline = createSplineFromBlenderSpline(bSplines[0])
            # is None when the spline type is not supported
            if spline is not None:
                if self.useWorldSpace:
                    spline.transform(self.object.matrix_world)
                return spline

        return BezierSpline()

    def setProperty(self, data):
        self.object, self.useWorldSpace = data

    def getProperty(self):
        return self.object, self.useWorldSpace

    def handleEyedropperButton(self, event):
        if event.ctrl:
            bpy.ops.an.rename_datablock_popup("INVOKE_DEFAULT",
                oldName = self.object.name,
                path = "bpy.data.objects",
                icon = "OUTLINER_OB_CURVE")
        else:
            object = bpy.context.active_object
            if getattr(object, "type", "") == "CURVE":
                self.object = object

    @classmethod
    def getDefaultValue(cls):
        return BezierSpline()

    @classmethod
    def getCopyExpression(cls):
        return "value.copy()"

    @classmethod
    def correctValue(cls, value):
        if isinstance(value, (BezierSpline, PolySpline)):
            return value, 0
        return cls.getDefaultValue(), 2


class SplineListSocket(bpy.types.NodeSocket, PythonListSocket):
    bl_idname = "an_SplineListSocket"
    bl_label = "Spline List Socket"
    dataType = "Spline List"
    baseType = SplineSocket
    drawColor = (0.8, 0.4, 1.0, 0.7)
    storable = True
    comparable = False

    object: PointerProperty(type = bpy.types.Object,
        description = "Use the splines from this object",
        update = propertyChanged)

    useWorldSpace: BoolProperty(default = True,
        description = "Convert points to world space",
        update = propertyChanged)

    def drawProperty(self, layout, text, node):
        row = layout.row(align = True)
        row.prop(self, "object", text = text)
        self.invokeFunction(row, node, "assignActiveObject", icon = "EYEDROPPER")
        if self.object:
            row.prop(self, "useWorldSpace", text = "", icon = "WORLD")

    def getValue(self):
        splines = createSplinesFromBlenderObject(self.object)
        if self.useWorldSpace:
            for spline in splines:
                spline.transform(self.object.matrix_world)
        return splines

    def setProperty(self, data):
        self.object, self.useWorldSpace = data

    def getProperty(self):
        return self.object, self.useWorldSpace


    def assignActiveObject(self):
        object = bpy.context.active_object
        if getattr(object, "type", "") == "CURVE":
            self.object = object

    @classmethod
    def getCopyExpression(cls):
        return "[element.copy() for element in value]"

    @classmethod
    def correctValue(cls, value):
        if isinstance(value, list):
            if all(isinstance(element, (BezierSpline, PolySpline)) for element in value):
                return value, 0
        return cls.getDefaultValue(), 2
