import bpy
from .. id_keys import getAllIDKeys
from .. utils.layout import splitAlignment
from .. utils.operators import makeOperator

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
        self.drawIDKeyHeader(box, object, key)
        object.id_keys.drawProperty(box, *key)
        object.id_keys.drawExtras(box, *key)

    def drawIDKeyHeader(self, layout, object, key):
        left, right = splitAlignment(layout)
        left.label(key.name)

        if object.id_keys.exists(*key):
            props = right.operator("an.remove_id_key_on_selected_objects", text = "Remove", icon = "X", emboss = False)
        else:
            props = right.operator("an.create_id_key_on_selected_objects", text = "Create", icon = "NEW", emboss = False)
        props.dataType = key.type
        props.propertyName = key.name

@makeOperator("an.create_id_key_on_selected_objects", "Create ID Keys", arguments = ["String", "String"])
def createIDKeyOnSelectedObjects(dataType, propertyName):
    for object in bpy.context.selected_objects:
        object.id_keys.create(dataType, propertyName)

@makeOperator("an.remove_id_key_on_selected_objects", "Remove ID Keys", arguments = ["String", "String"])
def createIDKeyOnSelectedObjects(dataType, propertyName):
    for object in bpy.context.selected_objects:
        object.id_keys.remove(dataType, propertyName)
