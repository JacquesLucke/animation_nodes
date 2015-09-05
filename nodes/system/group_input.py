import re
import bpy
from bpy.props import *
from ... sockets.info import toIdName
from ... events import networkChanged
from ... utils.layout import splitAlignment
from ... base_types.node import AnimationNode
from . subprogram_sockets import SubprogramData
from . utils import subprogramInterfaceChanged
from . subprogram_base import SubprogramBaseNode

class GroupInputNode(bpy.types.Node, AnimationNode, SubprogramBaseNode):
    bl_idname = "an_GroupInputNode"
    bl_label = "Group Input"

    def create(self):
        self.subprogramName = "Group"
        socket = self.outputs.new("an_NodeControlSocket", "New Parameter").margin = 0.15
        self.width = 180

    def draw(self, layout):
        layout.separator()
        layout.prop(self, "subprogramName", text = "", icon = "GROUP_VERTEX")
        if self.outputNode is None:
            self.invokeFunction(layout, "createGroupOutputNode", text = "Output Node", icon = "PLUS")

    def drawAdvanced(self, layout):
        col = layout.column()
        col.label("Description:")
        col.prop(self, "subprogramDescription", text = "")

        col = layout.column()
        col.label("Parameter Defaults:")
        box = col.box()
        for socket in list(self.outputs)[:-1]:
            socket.drawSocket(box, socket.text, drawType = "TEXT_PROPERTY_OR_NONE")

    def drawControlSocket(self, layout, socket):
        left, right = splitAlignment(layout)
        self.invokeSocketTypeChooser(left, "newParameter", icon = "ZOOMIN", emboss = False)
        right.label(socket.name)

    def edit(self):
        for target in self.newParameterSocket.dataTargets:
            if target.dataType == "Node Control": continue
            socket = self.newParameter(target.dataType, target.getDisplayedName(), target.getProperty())
            socket.linkWith(target)
        self.newParameterSocket.removeLinks()

    def newParameter(self, dataType, name = None, defaultValue = None):
        if name is None: name = dataType
        socket = self.outputs.new(toIdName(dataType), name, "parameter")
        if defaultValue is not None: socket.setProperty(defaultValue)
        socket.text = name
        socket.moveable = True
        socket.removeable = True
        socket.display.text = True
        socket.textProps.editable = True
        socket.display.textInput = True
        socket.display.removeOperator = True
        socket.moveUp()
        return socket

    def socketChanged(self):
        subprogramInterfaceChanged()

    def delete(self):
        self.outputs.clear()
        subprogramInterfaceChanged()

    def duplicate(self, sourceNode):
        match = re.search("(.*) ([0-9]+)$", self.subprogramName)
        if match: self.subprogramName = match.group(1) + " " + str(int(match.group(2)) + 1)
        else: self.subprogramName += " 2"

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
        bpy.ops.node.add_and_link_node("INVOKE_DEFAULT", use_transform = True, settings = settings, type = "an_GroupOutputNode")
