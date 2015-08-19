import bpy
from bpy.props import *
from ... base_types.node import AnimationNode

class GroupOutput(bpy.types.Node, AnimationNode):
    bl_idname = "an_GroupOutput"
    bl_label = "Group Output"

    groupInputIdentifier = StringProperty()

    def create(self):
        self.inputs.new("an_EmptySocket", "New Return")

    def draw(self, layout):
        layout.label("ID: " + self.groupInputIdentifier)

    def edit(self):
        dataOrigin = self.newReturnSocket.dataOriginSocket
        directOrigin = self.newReturnSocket.directOriginSocket

        if not dataOrigin: return
        if dataOrigin.dataType == "Empty": return
        socket = self.newReturn(dataOrigin.bl_idname, dataOrigin.getDisplayedName())
        socket.linkWith(directOrigin)
        socket.moveUp()
        self.newReturnSocket.removeConnectedLinks()

    def newReturn(self, idName, name):
        socket = self.inputs.new(idName, name, "return")
        socket.customName = name
        socket.moveable = True
        socket.removeable = True
        socket.nameSettings.display = True
        socket.nameSettings.editable = True
        socket.display.customNameInput = True
        socket.display.removeOperator = True
        return socket

    @property
    def newReturnSocket(self):
        return self.inputs[-1]
