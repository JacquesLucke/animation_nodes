import bpy
from bpy.props import *
from .. events import propertyChanged
from .. base_types.socket import AnimationNodeSocket
from .. data_structures.splines.bezier_spline import BezierSpline
from .. data_structures.splines.from_blender import createSplinesFromBlenderObject

class SplineSocket(bpy.types.NodeSocket, AnimationNodeSocket):
    bl_idname = "an_SplineSocket"
    bl_label = "Spline Socket"
    dataType = "Spline"
    allowedInputTypes = ["Spline"]
    drawColor = (0.74, 0.36, 1.0, 1.0)

    objectName = StringProperty(default = "",
        description = "Use the first spline from this object",
        update = propertyChanged)

    useWorldSpace = BoolProperty(default = True,
        description = "Convert points to world space",
        update = propertyChanged)

    showName = BoolProperty(default = True)
    showObjectInput = BoolProperty(default = True)

    def drawInput(self, layout, node, text):
        row = layout.row(align = True)
        if self.showName: row.label(text)
        if self.showObjectInput:
            row.prop_search(self, "objectName",  bpy.context.scene, "objects", icon="NONE", text = "")
            self.functionOperator(row, "assignActiveObject", icon = "EYEDROPPER")
            if self.objectName != "":
                row.prop(self, "useWorldSpace", text = "", icon = "WORLD")

    def getValue(self):
        object = bpy.data.objects.get(self.objectName)
        splines = createSplinesFromBlenderObject(object)
        if self.useWorldSpace:
            for spline in splines:
                spline.transform(object.matrix_world)
        if len(splines) > 0: return splines[0]
        else: return BezierSpline()

    def setStoreableValue(self, data):
        self.objectName, self.useWorldSpace = data

    def getStoreableValue(self):
        return self.objectName, self.useWorldSpace

    def getCopyValueFunctionString(self):
        return "return value.copy()"

    def assignActiveObject(self):
        object = bpy.context.active_object
        if getattr(object, "type", "") == "CURVE":
            self.objectName = object.name

    def toString(self):
        if self.showName: return self.getDisplayedName()
        if self.objectName == "": return "--None--"
        return self.objectName
