import bpy
from bpy.props import *
from ... events import treeChanged
from ... base_types import AnimationNode
from ... utils.layout import splitAlignment
from ... utils.names import getRandomString
from . subprogram_sockets import subprogramInterfaceChanged
from ... utils.nodes import newNodeAtCursor, invokeTranslation

class GroupOutputNode(AnimationNode, bpy.types.Node):
    bl_idname = "an_GroupOutputNode"
    bl_label = "Group Output"
    bl_width_default = 180
    onlySearchTags = True

    def inputNodeIdentifierChanged(self, context):
        subprogramInterfaceChanged()
        treeChanged()

    groupInputIdentifier: StringProperty(update = inputNodeIdentifierChanged)

    def setup(self):
        self.newInput("Node Control", "New Output", margin = 0.15)

    def draw(self, layout):
        if self.inInvalidNetwork:
            col = layout.column()
            col.scale_y = 1.5
            self.invokeFunction(col, "useGroupInputInNetwork", text = "Use Input in Network",
                description = "Scan the network of this node for group input nodes", icon = "QUESTION")

        layout.separator()

        inputNode = self.network.getGroupInputNode()
        if inputNode: layout.label(text = inputNode.subprogramName, icon = "GROUP_VERTEX")
        else: self.invokeFunction(layout, "createGroupInputNode", text = "Input Node", icon = "PLUS")
        layout.separator()


    def drawAdvanced(self, layout):
        layout.label(text = "Output Defaults:")
        box = layout.box()
        for socket in list(self.inputs)[:-1]:
            subBox = box.box()
            subBox.label(text = repr(socket.text))
            subBox.prop(socket.subprogram, "hideByDefault", text = "Hide")

    def drawControlSocket(self, layout, socket):
        left, right = splitAlignment(layout)
        left.label(text = socket.name)
        self.invokeSelector(right, "DATA_TYPE", "newGroupOutput",
            icon = "ADD", emboss = False)

    def edit(self):
        self.changeInputIdentifierIfNecessary()

        newOutputSocket = self.inputs[-1]
        dataOrigin = newOutputSocket.dataOrigin
        directOrigin = newOutputSocket.directOrigin

        if not dataOrigin: return
        if dataOrigin.dataType == "Node Control": return
        socket = self.newGroupOutput(dataOrigin.dataType, dataOrigin.getDisplayedName())
        socket.linkWith(directOrigin)
        newOutputSocket.removeLinks()

    def changeInputIdentifierIfNecessary(self):
        network = self.network
        if network.type != "Invalid": return
        if network.groupInAmount != 1: return
        inputNode = network.getGroupInputNode()
        if self.groupInputIdentifier == inputNode.identifier: return
        self.groupInputIdentifier = inputNode.identifier

    def newGroupOutput(self, dataType, name = None):
        if name is None: name = dataType
        socket = self.newInput(dataType, name, getRandomString(10))
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
        node = newNodeAtCursor("an_GroupInputNode")
        self.groupInputIdentifier = node.identifier
        invokeTranslation()

    def socketChanged(self):
        subprogramInterfaceChanged()

    def delete(self):
        self.clearSockets()
        subprogramInterfaceChanged()

    def useGroupInputInNetwork(self):
        network = self.network
        for node in network.getNodes():
            if node.bl_idname == "an_GroupInputNode":
                self.groupInputIdentifier = node.identifier
