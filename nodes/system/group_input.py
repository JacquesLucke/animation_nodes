import bpy
from bpy.props import *
from ... base_types.node import AnimationNode

class GroupInput(bpy.types.Node, AnimationNode):
    bl_idname = "an_GroupInput"
    bl_label = "Group Input"

    subprogramName = StringProperty(name = "Subprogram Name", default = "Group",
        description = "Subprogram name to identify this group elsewhere")

    def create(self):
        self.outputs.new("an_EmptySocket", "New Parameter")

    def draw(self, layout):
        layout.separator()
        layout.prop(self, "subprogramName", text = "", icon = "GROUP_VERTEX")

    def edit(self):
        for target in self.newParameterSocket.dataTargetSockets:
            if target.dataType == "Empty": continue
            socket = self.newParameter(target.bl_idname, target.getDisplayedName(), target.getStoreableValue())
            socket.linkWith(target)
            socket.moveUp()
        self.newParameterSocket.removeConnectedLinks()

    def newParameter(self, idName, name, defaultValue = None):
        socket = self.outputs.new(idName, name, "parameter")
        socket.setStoreableValue(defaultValue)
        socket.customName = name
        socket.moveable = True
        socket.removeable = True
        socket.nameSettings.display = True
        socket.nameSettings.editable = True
        socket.display.customNameInput = True
        socket.display.removeOperator = True
        return socket

    @property
    def newParameterSocket(self):
        return self.outputs[-1]
