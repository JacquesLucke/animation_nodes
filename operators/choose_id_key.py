import bpy
from bpy.props import *
from .. tree_info import getNodeByIdentifier
from .. id_keys import findIDKeysInCurrentFile
from .. utils.enum_items import enumItemsFromDicts

class IDKeySearch(bpy.types.Operator):
    bl_idname = "an.choose_id_key"
    bl_label = "ID Key Search"
    bl_options = {"REGISTER"}
    bl_property = "item"

    @enumItemsFromDicts
    def getSearchItems(self, context):
        for dataType, name in findIDKeysInCurrentFile():
            yield { "value" : dataType + " * " + name,
                    "name" : name }

    item = EnumProperty(items = getSearchItems)
    nodeIdentifier = StringProperty()
    callback = StringProperty()

    def invoke(self, context, event):
        context.window_manager.invoke_search_popup(self)
        return {"CANCELLED"}

    def execute(self, context):
        if self.item == "NONE": return {"CANCELLED"}
        node = getNodeByIdentifier(self.nodeIdentifier)
        dataType, name = self.item.split(" * ")
        getattr(node, self.callback)(dataType, name)
        return {"FINISHED"}
