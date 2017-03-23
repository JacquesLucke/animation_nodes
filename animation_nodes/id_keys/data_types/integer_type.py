import bpy
from bpy.props import *
from . base import SingleIDKeyDataType
from ... data_structures import LongLongList
from ... utils.blender_ui import getDpiFactor, redrawAll
from ... utils.selection import getSortedSelectedObjects

class IntegerDataType(SingleIDKeyDataType):
    identifier = "Integer"
    default = 0

    @classmethod
    def getList(cls, objects, name):
        default = cls.default
        path = cls.getPath(name)
        return LongLongList.fromValues(getattr(object, path, default) for object in objects)

    @classmethod
    def drawExtras(cls, layout, object, name):
        row = layout.row(align = True)
        props = row.operator("an.id_keys_from_selection_order", icon = "BORDER_RECT", text = "From Selection Order")
        props.offset = 0
        props.name = name
        props.showMenu = False

        props = row.operator("an.id_keys_from_selection_order", icon = "SETTINGS", text = "")
        props.name = name
        props.showMenu = True

class IDKeysFromSelectionOrder(bpy.types.Operator):
    bl_idname = "an.id_keys_from_selection_order"
    bl_label = "ID Keys from Selection Order"
    bl_description = "Assign integer ID Keys based on selection order."
    bl_options = {"INTERNAL"}

    name = StringProperty()
    showMenu = BoolProperty()
    offset = IntProperty(name = "Offset", default = 0)

    def invoke(self, context, event):
        if not self.showMenu:
            return self.execute(context)
        return context.window_manager.invoke_props_dialog(self, width = 200 * getDpiFactor())

    def draw(self, context):
        self.layout.prop(self, "offset")

    def check(self, context):
        return True

    def execute(self, context):
        for i, object in enumerate(getSortedSelectedObjects()):
            object.id_keys.set("Integer", self.name, i + self.offset)
        redrawAll()
        return {"FINISHED"}
