import bpy
from bpy.props import *
from .. tree_info import getNodeByIdentifier
from .. sockets.info import getDataTypeItems, getListDataTypeItems

socketGroupItems = [
    ("ALL", "All", ""),
    ("LIST", "List", "") ]

class ChooseSocketType(bpy.types.Operator):
    bl_idname = "an.choose_socket_type"
    bl_label = "Choose Socket Type"
    bl_property = "selectedDataType"

    def getItems(self, context):
        if self.socketGroup == "ALL":
            return getDataTypeItems()
        if self.socketGroup == "LIST":
            return getListDataTypeItems()

    selectedDataType = EnumProperty(items = getItems)
    socketGroup = EnumProperty(items = socketGroupItems)

    nodeIdentifier = StringProperty()
    callback = StringProperty()

    def invoke(self, context, event):
        context.window_manager.invoke_search_popup(self)
        return {"CANCELLED"}

    def execute(self, context):
        node = getNodeByIdentifier(self.nodeIdentifier)
        function = getattr(node, self.callback)
        function(self.selectedDataType)
        return {"FINISHED"}
