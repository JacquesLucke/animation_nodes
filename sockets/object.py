import bpy
from bpy.props import *
from .. events import propertyChanged
from .. base_types.socket import AnimationNodeSocket

class ObjectSocket(bpy.types.NodeSocket, AnimationNodeSocket):
    bl_idname = "an_ObjectSocket"
    bl_label = "Object Socket"
    dataType = "Object"
    allowedInputTypes = ["Object"]
    drawColor = (0, 0, 0, 1)

    objectName = StringProperty(update = propertyChanged)
    showName = BoolProperty(default = True)
    objectCreationType = StringProperty(default = "")

    def drawInput(self, layout, node, text):
        col = layout.column()
        row = col.row(align = True)
        if self.showName:
            row.label(text)
        row.prop_search(self, "objectName",  bpy.context.scene, "objects", icon="NONE", text = "")

        if self.objectCreationType != "":
            self.callFunctionFromUI(row, "createObject", icon = "PLUS")

        self.callFunctionFromUI(row, "assignActiveObject", icon = "EYEDROPPER")

    def getValue(self):
        return bpy.data.objects.get(self.objectName)

    def setStoreableValue(self, data):
        self.objectName = data

    def getStoreableValue(self):
        return self.objectName

    def assignActiveObject(self):
        object = bpy.context.active_object
        if object:
            self.objectName = object.name

    def createObject(self):
        type = self.objectCreationType
        if type == "MESH": data = bpy.data.meshes.new("Mesh")
        if type == "CURVE":
            data = bpy.data.curves.new("Curve", "CURVE")
            data.dimensions = "3D"
            data.fill_mode = "FULL"
        object = bpy.data.objects.new("Target", data)
        bpy.context.scene.objects.link(object)
        self.objectName = object.name

    def toString(self):
        if self.showName: return self.getDisplayedName()
        return self.objectName
