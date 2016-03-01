import bpy
from bpy.props import *
from .. events import propertyChanged
from .. base_types.socket import AnimationNodeSocket
from .. utils.id_reference import tryToFindObjectReference

class ObjectSocket(bpy.types.NodeSocket, AnimationNodeSocket):
    bl_idname = "an_ObjectSocket"
    bl_label = "Object Socket"
    dataType = "Object"
    allowedInputTypes = ["Object"]
    drawColor = (0, 0, 0, 1)
    storable = False
    hashable = True

    objectName = StringProperty(update = propertyChanged)
    objectCreationType = StringProperty(default = "")

    def drawProperty(self, layout, text):
        row = layout.row(align = True)
        row.prop_search(self, "objectName",  bpy.context.scene, "objects", icon="NONE", text = text)

        if self.objectCreationType != "":
            self.invokeFunction(row, "createObject", icon = "PLUS")

        self.invokeFunction(row, "assignActiveObject", icon = "EYEDROPPER")

    def getValue(self):
        if self.objectName == "": return None

        object = tryToFindObjectReference(self.objectName)
        name = getattr(object, "name", "")
        if name != self.objectName: self.objectName = name
        return object

    def setProperty(self, data):
        self.objectName = data

    def getProperty(self):
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
