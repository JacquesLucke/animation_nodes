import bpy
from bpy.props import *
from ... events import treeChanged
from . utils import updateCallerNodes
from ... base_types.node import AnimationNode

class GroupOutput(bpy.types.Node, AnimationNode):
    bl_idname = "an_GroupOutput"
    bl_label = "Group Output"

    def inputNodeIdentifierChanged(self, context):
        treeChanged()

    groupInputIdentifier = StringProperty(update = inputNodeIdentifierChanged)

    def create(self):
        self.inputs.new("an_EmptySocket", "New Return")

    def draw(self, layout):
        inputNode = self.network.groupInputNode
        if inputNode: layout.label("Group: " + inputNode.subprogramName)
        else: self.functionOperator(layout, "createGroupInputNode", text = "Input Node", icon = "PLUS")

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

    def createGroupInputNode(self):
        bpy.ops.node.add_and_link_node(type = "an_GroupInput")
        node = self.nodeTree.nodes[-1]
        self.groupInputIdentifier = node.identifier
        bpy.ops.node.translate_attach("INVOKE_DEFAULT")

    def socketChanged(self):
        self.updateCallerNodes()

    def delete(self):
        self.inputs.clear()
        self.updateCallerNodes()

    def updateCallerNodes(self):
        updateCallerNodes(self.groupInputIdentifier)

    @property
    def newReturnSocket(self):
        return self.inputs[-1]

    @property
    def groupInput(self):
        return self.network.groupInputNode
