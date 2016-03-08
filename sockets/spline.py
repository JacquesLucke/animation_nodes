import bpy
from bpy.props import *
from .. events import propertyChanged
from .. base_types.socket import AnimationNodeSocket
from .. utils.id_reference import tryToFindObjectReference
from .. data_structures.splines.bezier_spline import BezierSpline
from .. data_structures.splines.from_blender import createSplinesFromBlenderObject

class SplineSocket(bpy.types.NodeSocket, AnimationNodeSocket):
    bl_idname = "an_SplineSocket"
    bl_label = "Spline Socket"
    dataType = "Spline"
    allowedInputTypes = ["Spline"]
    drawColor = (0.8, 0.4, 1.0, 1.0)
    storable = True
    comparable = False

    objectName = StringProperty(default = "",
        description = "Use the first spline from this object",
        update = propertyChanged)

    useWorldSpace = BoolProperty(default = True,
        description = "Convert points to world space",
        update = propertyChanged)

    showObjectInput = BoolProperty(default = True)

    def drawProperty(self, layout, text):
        row = layout.row(align = True)
        row.prop_search(self, "objectName",  bpy.context.scene, "objects", icon="NONE", text = text)
        self.invokeFunction(row, "assignActiveObject", icon = "EYEDROPPER")
        if self.objectName != "":
            row.prop(self, "useWorldSpace", text = "", icon = "WORLD")

    def getValue(self):
        object = self.getObject()
        splines = createSplinesFromBlenderObject(object)
        if self.useWorldSpace:
            for spline in splines:
                spline.transform(object.matrix_world)
        if len(splines) > 0: return splines[0]
        else: return BezierSpline()

    def getObject(self):
        if self.objectName == "": return None

        object = tryToFindObjectReference(self.objectName)
        name = getattr(object, "name", "")
        if name != self.objectName: self.objectName = name
        return object

    def setProperty(self, data):
        self.objectName, self.useWorldSpace = data

    def getProperty(self):
        return self.objectName, self.useWorldSpace

    def updateProperty(self):
        self.getObject()

    def getCopyExpression(self):
        return "value.copy()"

    def assignActiveObject(self):
        object = bpy.context.active_object
        if getattr(object, "type", "") == "CURVE":
            self.objectName = object.name
