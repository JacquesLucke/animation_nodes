import bpy
from bpy.props import *
from ... events import treeChanged
from ... base_types.node import AnimationNode
from . subprogram_sockets import SubprogramData

class GroupInput(bpy.types.Node, AnimationNode):
    bl_idname = "an_GroupInput"
    bl_label = "Group Input"

    def subprogramNameChanged(self, context):
        treeChanged()

    subprogramName = StringProperty(name = "Subprogram Name", default = "Group",
        description = "Subprogram name to identify this group elsewhere",
        update = subprogramNameChanged)

    def create(self):
        self.outputs.new("an_EmptySocket", "New Parameter")

    def draw(self, layout):
        layout.separator()
        layout.prop(self, "subprogramName", text = "", icon = "GROUP_VERTEX")
        if self.outputNode is None:
            self.functionOperator(layout, "createGroupOutputNode", text = "Output Node", icon = "PLUS")

    def drawAdvanced(self, layout):
        for socket in list(self.outputs)[:-1]:
            socket.drawInput(layout, self, socket.getDisplayedName())

    def edit(self):
        for target in self.newParameterSocket.dataTargetSockets:
            if target.dataType == "Empty": continue
            socket = self.newParameter(target.bl_idname, target.getDisplayedName(), target.getStoreableValue())
            socket.linkWith(target)
            socket.moveUp()
        self.newParameterSocket.removeConnectedLinks()

    def newParameter(self, idName, name, defaultValue):
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

    def getSocketData(self):
        data = SubprogramData()

        for socket in self.outputs[:-1]:
            data.newInputFromSocket(socket)

        if self.outputNode is not None:
            for socket in self.outputNode.inputs[:-1]:
                data.newOutputFromSocket(socket)

        return data

    @property
    def newParameterSocket(self):
        return self.outputs[-1]

    @property
    def outputNode(self):
        return self.network.groupOutputNode

    def createGroupOutputNode(self):
        settings = [{"name" : "groupInputIdentifier", "value" : repr(self.identifier)}]
        bpy.ops.node.add_and_link_node("INVOKE_DEFAULT", use_transform = True, settings = settings, type = "an_GroupOutput")
