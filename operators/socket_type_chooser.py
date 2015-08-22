import bpy
from bpy.props import *
from .. sockets.info import getSocketClasses
from .. tree_info import getNodeByIdentifier
from .. utils.enum_items import enumItemsFromList

socketGroupItems = [
    ("ALL", "All", "") ]

class ChooseSocketType(bpy.types.Operator):
    bl_idname = "an.choose_socket_type"
    bl_label = "Choose Socket Type"
    bl_property = "selectedDataType"

    @enumItemsFromList
    def getItems(self, context):
        if self.socketGroup == "ALL":
            dataTypes = [socket.dataType for socket in getSocketClasses()]
            dataTypes.remove("Node Control")
            return dataTypes

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
