import bpy
from bpy.props import *
from bpy.types import Object
from .. events import propertyChanged
from .. base_types import AnimationNodeSocket, PythonListSocket

class ObjectSocket(bpy.types.NodeSocket, AnimationNodeSocket):
    bl_idname = "an_ObjectSocket"
    bl_label = "Object Socket"
    dataType = "Object"
    drawColor = (0, 0, 0, 1)
    storable = False
    comparable = True

    object: PointerProperty(type = Object, update = propertyChanged)
    objectCreationType: StringProperty(default = "")
    showHideToggle: BoolProperty(default = False)

    def drawProperty(self, layout, text, node):
        row = layout.row(align = True)
        row.prop(self, "object", text = text)

        if self.objectCreationType != "":
            self.invokeFunction(row, node, "createObject", icon = "PLUS")

        if self.showHideToggle:
            if self.object is not None:
                icon = "RESTRICT_VIEW_ON" if self.object.hide_viewport else "RESTRICT_VIEW_OFF"
                self.invokeFunction(row, node, "toggleObjectVisibilty", icon = icon,
                    description = "Toggle viewport and render visibility.")

        self.invokeFunction(row, node, "handleEyedropperButton", icon = "EYEDROPPER", passEvent = True,
            description = "Assign active object to this socket (hold CTRL to open a rename object dialog)")

    def getValue(self):
        return self.object

    def setProperty(self, data):
        self.object = data

    def getProperty(self):
        return self.object

    def handleEyedropperButton(self, event):
        if event.ctrl:
            bpy.ops.an.rename_datablock_popup("INVOKE_DEFAULT",
                oldName = self.object.name,
                path = "bpy.data.objects",
                icon = "OBJECT_DATA")
        else:
            object = bpy.context.active_object
            if object: self.object = object

    def createObject(self):
        type = self.objectCreationType
        if type == "MESH": data = bpy.data.meshes.new("Mesh")
        if type == "CURVE":
            data = bpy.data.curves.new("Curve", "CURVE")
            data.dimensions = "3D"
            data.fill_mode = "FULL"
        object = bpy.data.objects.new("Target", data)
        bpy.context.collection.objects.link(object)
        self.object = object

    def toggleObjectVisibilty(self):
        if self.object is None: return
        self.object.hide_viewport = not self.object.hide_viewport
        self.object.hide_render = self.object.hide_viewport

    @classmethod
    def getDefaultValue(cls):
        return None

    @classmethod
    def correctValue(cls, value):
        if isinstance(value, Object) or value is None:
            return value, 0
        return cls.getDefaultValue(), 2


class ObjectListSocket(bpy.types.NodeSocket, PythonListSocket):
    bl_idname = "an_ObjectListSocket"
    bl_label = "Object List Socket"
    dataType = "Object List"
    baseType = ObjectSocket
    drawColor = (0, 0, 0, 0.5)
    storable = False
    comparable = False

    @classmethod
    def getCopyExpression(cls):
        return "value[:]"

    @classmethod
    def correctValue(cls, value):
        if isinstance(value, list):
            if all(isinstance(element, Object) or element is None for element in value):
                return value, 0
        return cls.getDefaultValue(), 2
