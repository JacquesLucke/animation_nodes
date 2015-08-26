import bpy
from bpy.props import *
from ... base_types.node import AnimationNode
from ... tree_info import getNodeByIdentifier

class UpdateLoopParameterNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_UpdateLoopParameterNode"
    bl_label = "Update Loop Parameter"

    def identifierChanged(self, context):
        socket = self.linkedParameterSocket
        if socket:
            self.parameterIdName = self.linkedParameterSocket.bl_idname
            self.generateSocket()

    loopInputIdentifier = StringProperty(update = identifierChanged)
    parameterIdentifier = StringProperty(update = identifierChanged)
    parameterIdName = StringProperty()

    def create(self):
        self.width = 180

    def draw(self, layout):
        socket = self.linkedParameterSocket
        if socket:
            layout.label("{} > {}".format(repr(socket.node.subprogramName), socket.text), icon = "GROUP_VERTEX")
        else:
            layout.label("Target does not exist", icon = "ERROR")

    def generateSocket(self):
        self.inputs.clear()
        socket = self.inputs.new(self.parameterIdName, "New Value", "newValue")
        socket.display.nameOnly = True

    @property
    def linkedParameterSocket(self):
        try:
            inputNode = self.loopInputNode
            return inputNode.outputsByIdentifier[self.parameterIdentifier]
        except: pass

    @property
    def loopInputNode(self):
        try: return getNodeByIdentifier(self.loopInputIdentifier)
        except: return None
