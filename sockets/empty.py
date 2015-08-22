import bpy
from bpy.props import *
from . info import getSocketClasses
from .. utils.nodes import getSocket
from .. utils.enum_items import enumItemsFromList
from .. base_types.socket import AnimationNodeSocket

class EmptySocket(bpy.types.NodeSocket, AnimationNodeSocket):
    bl_idname = "an_EmptySocket"
    bl_label = "Empty Socket"
    dataType = "Empty"
    allowedInputTypes = ["all"]
    drawColor = (0.0, 0.0, 0.0, 0.0)

    passiveType = StringProperty(default = "")

    socketGroup = StringProperty(default = "")
    newSocketCallback = StringProperty(default = "")
    emboss = BoolProperty(default = True)

    def drawInput(self, layout, node, text):
        if self.newSocketCallback == "":
            layout.label(text)
        elif self.socketGroup != "":
            self.functionOperator(layout, "chooseSocketType", text = text, emboss = self.emboss)
        else:
            self.functionOperator(layout, "callNewSocketCallback", text = text, emboss = self.emboss)

    def getValue(self):
        return None

    def chooseSocketType(self):
        bpy.ops.an.choose_socket_type("INVOKE_DEFAULT",
            treeName = self.nodeTree.name, nodeName = self.node.name,
            isOutput = self.isOutput, identifier = self.identifier,
            socketGroup = self.socketGroup)

    def socketTypeChoosed(self, dataType):
        function = getattr(self.node, self.newSocketCallback)
        function(dataType)

    def callNewSocketCallback(self):
        function = getattr(self.node, self.newSocketCallback)
        function()


socketGroupItems = [
    ("ALL", "All", "")
]

class ChooseSocketType(bpy.types.Operator):
    bl_idname = "an.choose_socket_type"
    bl_label = "Choose Socket Type"
    bl_property = "item"

    @enumItemsFromList
    def getItems(self, context):
        if self.socketGroup == "ALL":
            dataTypes = [socket.dataType for socket in getSocketClasses()]
            dataTypes.remove("Empty")
            return dataTypes

    item = EnumProperty(items = getItems)
    socketGroup = EnumProperty(items = socketGroupItems)

    treeName = StringProperty()
    nodeName = StringProperty()
    isOutput = BoolProperty()
    identifier = StringProperty()

    def invoke(self, context, event):
        context.window_manager.invoke_search_popup(self)
        return {"CANCELLED"}

    def execute(self, context):
        socket = getSocket(self.treeName, self.nodeName, self.isOutput, self.identifier)
        socket.socketTypeChoosed(self.item)
        return {"FINISHED"}
