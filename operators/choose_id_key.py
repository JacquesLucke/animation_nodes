import bpy
from bpy.props import *
from .. id_keys import findIDKeysInCurrentFile
from .. utils.enum_items import enumItemsFromDicts

class IDKeySearch(bpy.types.Operator):
    bl_idname = "an.choose_id_key"
    bl_label = "ID Key Search"
    bl_options = {"REGISTER"}
    bl_property = "item"

    def getSearchItems(self, context):
        itemDict = []
        for dataType, name in findIDKeysInCurrentFile():
            itemDict.append({"value" : dataType + " * " + name, "name" : name})
        return enumItemsFromDicts(itemDict)

    item = EnumProperty(items = getSearchItems)
    callback = StringProperty()

    def invoke(self, context, event):
        context.window_manager.invoke_search_popup(self)
        return {"CANCELLED"}

    def execute(self, context):
        if self.item == "NONE": return {"CANCELLED"}
        dataType, name = self.item.split(" * ")
        self.executeCallback(self.callback, dataType, name)
        return {"FINISHED"}
