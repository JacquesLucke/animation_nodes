import bpy
from bpy.props import *
from .. tree_info import getNodeByIdentifier
from .. utils.enum_items import cacheEnumItems
from .. sockets.info import getDataTypeItems, getListDataTypeItems, getDrawableDataTypeItems

socketGroupItems = [
    ("ALL", "All", ""),
    ("LIST", "List", ""),
    ("DRAWABLE", "Drawable", ""),]

class ChooseSocketType(bpy.types.Operator):
    bl_idname = "an.choose_socket_type"
    bl_label = "Choose Socket Type"
    bl_property = "selectedDataType"

    def getItems(self, context):
        if self.socketGroup == "ALL":
            return getDataTypeItems(skipInternalTypes = True)
        if self.socketGroup == "LIST":
            return getListDataTypeItems()
        if self.socketGroup == "DRAWABLE":
            return getDrawableDataTypeItems()

    selectedDataType: EnumProperty(items = cacheEnumItems(getItems))
    socketGroup: EnumProperty(items = socketGroupItems)

    callback: StringProperty()

    def invoke(self, context, event):
        context.window_manager.invoke_search_popup(self)
        return {"CANCELLED"}

    def execute(self, context):
        self.an_executeCallback(self.callback, self.selectedDataType)
        return {"FINISHED"}
