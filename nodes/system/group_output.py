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
        self.width = 180

    def draw(self, layout):
        if self.inInvalidNetwork:
            col = layout.column()
            col.scale_y = 1.5
            self.functionOperator(col, "useGroupInputInNetwork", text = "Use Input in Network",
                description = "Scan the network of this node for group input nodes", icon = "QUESTION")

        layout.separator()

        inputNode = self.network.groupInputNode
        if inputNode: layout.label(inputNode.subprogramName, icon = "GROUP_VERTEX")
        else: self.functionOperator(layout, "createGroupInputNode", text = "Input Node", icon = "PLUS")
        layout.separator()

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
        socket.displayCustomName = True
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

    def useGroupInputInNetwork(self):
        network = self.network
        for node in network.getNodes():
            if node.bl_idname == "an_GroupInput":
                self.groupInputIdentifier = node.identifier

    @property
    def newReturnSocket(self):
        return self.inputs[-1]
