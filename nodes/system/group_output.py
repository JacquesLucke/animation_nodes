import bpy
from bpy.props import *
from ... events import treeChanged
from ... sockets.info import toIdName
from ... base_types.node import AnimationNode
from . utils import updateSubprogramInvokerNodes

class GroupOutputNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_GroupOutputNode"
    bl_label = "Group Output"

    def inputNodeIdentifierChanged(self, context):
        treeChanged()

    groupInputIdentifier = StringProperty(update = inputNodeIdentifierChanged)

    def create(self):
        socket = self.inputs.new("an_NodeControlSocket", "New Return")
        socket.drawCallback = "drawNewReturnSocket"
        socket.margin = 0.15
        self.width = 180

    def draw(self, layout):
        if self.inInvalidNetwork:
            col = layout.column()
            col.scale_y = 1.5
            self.invokeFunction(col, "useGroupInputInNetwork", text = "Use Input in Network",
                description = "Scan the network of this node for group input nodes", icon = "QUESTION")

        layout.separator()

        inputNode = self.network.groupInputNode
        if inputNode: layout.label(inputNode.subprogramName, icon = "GROUP_VERTEX")
        else: self.invokeFunction(layout, "createGroupInputNode", text = "Input Node", icon = "PLUS")
        layout.separator()

    def drawNewReturnSocket(self, layout):
        row = layout.row()
        subrow = row.row()
        subrow.alignment = "LEFT"
        subrow.label("New Return")
        subrow = row.row()
        subrow.alignment = "RIGHT"
        self.invokeFunction(subrow, "chooseNewReturnType", icon = "ZOOMIN", emboss = False)

    def chooseNewReturnType(self):
        self.chooseSocketDataType("newReturn")

    def edit(self):
        dataOrigin = self.newReturnSocket.dataOrigin
        directOrigin = self.newReturnSocket.directOrigin

        if not dataOrigin: return
        if dataOrigin.dataType == "Node Control": return
        socket = self.newReturn(dataOrigin.dataType, dataOrigin.getDisplayedName())
        socket.linkWith(directOrigin)
        self.newReturnSocket.removeLinks()

    def newReturn(self, dataType, name = None):
        if name is None: name = dataType
        socket = self.inputs.new(toIdName(dataType), name, "return")
        socket.dataIsModified = True
        socket.text = name
        socket.moveable = True
        socket.removeable = True
        socket.display.text = True
        socket.textProps.editable = True
        socket.display.textInput = True
        socket.display.removeOperator = True
        socket.moveUp()
        return socket

    def createGroupInputNode(self):
        bpy.ops.node.add_and_link_node(type = "an_GroupInputNode")
        node = self.nodeTree.nodes[-1]
        self.groupInputIdentifier = node.identifier
        bpy.ops.node.translate_attach("INVOKE_DEFAULT")

    def socketChanged(self):
        updateSubprogramInvokerNodes()

    def delete(self):
        self.inputs.clear()
        updateSubprogramInvokerNodes()

    def useGroupInputInNetwork(self):
        network = self.network
        for node in network.getNodes():
            if node.bl_idname == "an_GroupInputNode":
                self.groupInputIdentifier = node.identifier

    @property
    def newReturnSocket(self):
        return self.inputs[-1]
