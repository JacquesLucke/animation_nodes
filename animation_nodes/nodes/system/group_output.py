import bpy
from bpy.props import *
from ... events import treeChanged
from ... utils.layout import splitAlignment
from ... base_types import AnimationNode
from . subprogram_sockets import subprogramInterfaceChanged
from ... utils.nodes import newNodeAtCursor, invokeTranslation

class GroupOutputNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_GroupOutputNode"
    bl_label = "Group Output"
    bl_width_default = 180

    def inputNodeIdentifierChanged(self, context):
        subprogramInterfaceChanged()
        treeChanged()

    groupInputIdentifier = StringProperty(update = inputNodeIdentifierChanged)

    def setup(self):
        socket = self.newInput("an_NodeControlSocket", "New Return").margin = 0.15

    def draw(self, layout):
        if self.inInvalidNetwork:
            col = layout.column()
            col.scale_y = 1.5
            self.invokeFunction(col, "useGroupInputInNetwork", text = "Use Input in Network",
                description = "Scan the network of this node for group input nodes", icon = "QUESTION")

        layout.separator()

        inputNode = self.network.getGroupInputNode()
        if inputNode: layout.label(inputNode.subprogramName, icon = "GROUP_VERTEX")
        else: self.invokeFunction(layout, "createGroupInputNode", text = "Input Node", icon = "PLUS")
        layout.separator()

    def drawControlSocket(self, layout, socket):
        left, right = splitAlignment(layout)
        left.label(socket.name)
        self.invokeSocketTypeChooser(right, "newReturn", icon = "ZOOMIN", emboss = False)

    def edit(self):
        self.changeInputIdentifierIfNecessary()

        dataOrigin = self.newReturnSocket.dataOrigin
        directOrigin = self.newReturnSocket.directOrigin

        if not dataOrigin: return
        if dataOrigin.dataType == "Node Control": return
        socket = self.newReturn(dataOrigin.dataType, dataOrigin.getDisplayedName())
        socket.linkWith(directOrigin)
        self.newReturnSocket.removeLinks()

    def changeInputIdentifierIfNecessary(self):
        network = self.network
        if network.type != "Invalid": return
        if network.groupInAmount != 1: return
        inputNode = network.getGroupInputNode()
        if self.groupInputIdentifier == inputNode.identifier: return
        self.groupInputIdentifier = inputNode.identifier

    def newReturn(self, dataType, name = None):
        if name is None: name = dataType
        socket = self.newInput(dataType, name, "return")
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

    def getTemplateCode(self):
        for socket in self.inputs[:-1]:
            yield "self.newReturn({}, name = {})".format(repr(socket.dataType), repr(socket.text))

    @property
    def newReturnSocket(self):
        return self.inputs[-1]
