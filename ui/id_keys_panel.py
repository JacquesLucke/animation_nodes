import bpy
from .. id_keys import getAllIDKeys

class IDKeyPanel(bpy.types.Panel):
    bl_idname = "an_id_keys_panel"
    bl_label = "ID Keys"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_category = "AN"

    def draw(self, context):
        object = context.active_object
        if object is None:
            self.layout.label("Select an object", icon = "INFO")
        else:
            self.drawForObject(self.layout, object)

    def drawForObject(self, layout, object):
        layout.operator("an.update_id_keys_list")
        for key in getAllIDKeys():
            self.drawIdKey(layout, object, key)

    def drawIdKey(self, layout, object, key):
        box = layout.box()

        exists = object.id_keys.exists(*key)
        icon = "FILE_TICK" if exists else "NEW"
        box.label("{} ({})".format(key.name, key.type), icon = icon)

        object.id_keys.drawProperty(box, *key)
