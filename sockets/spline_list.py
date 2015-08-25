import bpy
from bpy.props import *
from .. events import propertyChanged
from .. base_types.socket import AnimationNodeSocket
from .. data_structures.splines.from_blender import createSplinesFromBlenderObject

class SplineListSocket(bpy.types.NodeSocket, AnimationNodeSocket):
    bl_idname = "an_SplineListSocket"
    bl_label = "Spline List Socket"
    dataType = "Spline List"
    allowedInputTypes = ["Spline List"]
    drawColor = (0.5, 0.28, 1.0, 1.0)

    objectName = StringProperty(default = "",
        description = "Use the splines from this object",
        update = propertyChanged)

    useWorldSpace = BoolProperty(default = True,
        description = "Convert points to world space",
        update = propertyChanged)

    showName = BoolProperty(default = True)
    showObjectInput = BoolProperty(default = True)

    def drawInput(self, layout, node, text):
        if not self.showName: text = ""
        if self.showObjectInput: self.drawAsProperty(layout, text)
        else: self.label(text)

    def drawAsProperty(self, layout, text):
        row = layout.row(align = True)
        row.prop_search(self, "objectName",  bpy.context.scene, "objects", icon="NONE", text = text)
        self.invokeFunction(row, "assignActiveObject", icon = "EYEDROPPER")
        if self.objectName != "":
            row.prop(self, "useWorldSpace", text = "", icon = "WORLD")

    def getValue(self):
        object = bpy.data.objects.get(self.objectName)
        splines = createSplinesFromBlenderObject(object)
        if self.useWorldSpace:
            for spline in splines:
                spline.transform(object.matrix_world)
        return splines

    def setStoreableValue(self, data):
        self.objectName, self.useWorldSpace = data

    def getStoreableValue(self):
        return (self.objectName, self.useWorldSpace)

    def getCopyStatement(self):
        return "[element.copy() for element in value]"

    def assignActiveObject(self):
        object = bpy.context.active_object
        if getattr(object, "type", "") == "CURVE":
            self.objectName = object.name
