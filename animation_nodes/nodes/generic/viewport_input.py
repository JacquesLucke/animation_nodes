import bpy
from bpy.props import *
from ... base_types import AnimationNode
from ... utils.names import getRandomString

class ViewportInputNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_ViewportInputNode"
    bl_label = "Viewport Input"

    hidden: BoolProperty(default = False)
    orderWeight: IntProperty(name = "Order Weight", default = 0,
        description = "The weight to use for ordering. Lower weights puts the node at the top")

    def setup(self):
        self.label = "Viewport Input"
        self.newOutput("Node Control", "New Output", margin = 0.15)

    def drawControlSocket(self, layout, socket):
        self.invokeSelector(layout, "DATA_TYPE", "newOutputSocket", text = "New Output",
            description = "Create a new output socket", icon = "ADD", emboss = False,
            dataTypes = "DRAWABLE")

    def drawAdvanced(self, layout):
        layout.prop(self, "orderWeight")

    def getExecutionCode(self, required):
        for i, output in enumerate(self.outputs[:-1]):
            yield f"{output.identifier} = self.outputs[{i}].getValue()"

    def edit(self):
        for target in self.outputs[-1].dataTargets:
            if target.dataType == "Node Control": continue
            socket = self.newOutputSocket(target.dataType, target.getDisplayedName(), target.getProperty())
            socket.linkWith(target)
        self.outputs[-1].removeLinks()

    def newOutputSocket(self, dataType, name = None, defaultValue = None):
        if name is None: name = dataType
        socket = self.newOutput(dataType, name, getRandomString(10))
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
