import bpy
from bpy.props import *
from .. events import treeChanged
from .. old_utils import getRandomString, isSocketLinked
from . socket_function_call import getSocketFunctionCallOperatorName
from .. utils.names import toVariableName

class an_CustomNameProperties(bpy.types.PropertyGroup):
    unique = BoolProperty(default = False)
    display = BoolProperty(default = False)
    editable = BoolProperty(default = False)
    variable = BoolProperty(default = False)
    callAfterChange = BoolProperty(default = False)

class AnimationNodeSocket:

    def customNameChanged(self, context):
        updateCustomName(self)

    customName = StringProperty(default = "custom name", update = customNameChanged)
    nameSettings = PointerProperty(type = an_CustomNameProperties)

    removeable = BoolProperty(default = False)
    callNodeToRemove = BoolProperty(default = False)
    moveable = BoolProperty(default = False)
    moveGroup = IntProperty(default = 0)

    def draw(self, context, layout, node, text):
        displayText = self.getDisplayedName()

        row = layout.row(align = True)
        if self.nameSettings.editable:
            row.prop(self, "customName", text = "")
        else:
            if not self.is_output and not isSocketLinked(self):
                self.drawInput(row, node, displayText)
            else:
                if self.is_output: row.alignment = "RIGHT"
                row.label(displayText)

        if self.moveable:
            row.separator()
            self.callFunctionFromUI(row, "moveSocketUp", icon = "TRIA_UP")
            self.callFunctionFromUI(row, "moveSocketDown", icon = "TRIA_DOWN")

        if self.removeable:
            row.separator()
            self.callFunctionFromUI(row, "removeSocket", icon = "X")

    def getDisplayedName(self):
        if self.nameSettings.display or self.nameSettings.editable: return self.customName
        return self.name

    def draw_color(self, context, node):
        return self.drawColor

    def setStoreableValue(self, data):
        pass

    def getStoreableValue(self):
        return

    def callFunctionFromUI(self, layout, functionName, text = "", icon = "NONE", description = ""):
        idName = getSocketFunctionCallOperatorName(description)
        props = layout.operator(idName, text = text, icon = icon)
        props.nodeTreeName = self.node.id_data.name
        props.nodeName = self.node.name
        props.isOutput = self.is_output
        props.identifier = self.identifier
        props.functionName = functionName

    def moveSocketUp(self):
        self.moveSocket(moveUp = True)

    def moveSocketDown(self):
        self.moveSocket(moveUp = False)

    def moveSocket(self, moveUp = True):
        moveableSocketIndices = [index for index, socket in enumerate(self.sockets) if socket.moveable and socket.moveGroup == self.moveGroup]
        currentIndex = list(self.sockets).index(self)

        targetIndex = -1
        for index in moveableSocketIndices:
            if moveUp and index < currentIndex:
                targetIndex = index
            if not moveUp and index > currentIndex:
                targetIndex = index
                break

        if targetIndex != -1:
            self.sockets.move(currentIndex, targetIndex)
            if moveUp: self.sockets.move(targetIndex + 1, currentIndex)
        else: self.sockets.move(targetIndex - 1, currentIndex)
        return {'FINISHED'}

    def removeSocket(self):
        if self.callNodeToRemove:
            self.node.removeSocket(socket)
        else:
            self.sockets.remove(self)

    @property
    def sockets(self):
        """Returns all sockets next to this one (all inputs or outputs)"""
        return self.node.outputs if self.is_output else self.node.inputs




isUpdating = False
def updateCustomName(socket):
    global isUpdating
    if not isUpdating:
        isUpdating = True
        correctCustomName(socket)
        treeChanged()
        isUpdating = False

def correctCustomName(socket):
    if socket.nameSettings.variable:
        socket.customName = toVariableName(socket.customName)
    if socket.nameSettings.unique:
        customName = socket.customName
        socket.customName = "temporary name to avoid some errors"
        socket.customName = getNotUsedCustomName(socket.node, prefix = customName)
    if socket.nameSettings.callAfterChange:
        socket.node.customSocketNameChanged(socket)

def getNotUsedCustomName(node, prefix):
    customName = prefix
    while isCustomNameUsed(node, customName):
        customName = prefix + getRandomString(3)
    return customName

def isCustomNameUsed(node, name):
    for socket in node.inputs:
        if socket.customName == name: return True
    for socket in node.outputs:
        if socket.customName == name: return True
    return False



# Register
##################################

def getSocketVisibility(socket):
    return not socket.hide

def setSocketVisibility(socket, value):
    socket.hide = not value


def register():
    bpy.types.NodeSocket.show = BoolProperty(default = True, get = getSocketVisibility, set = setSocketVisibility)

def unregister():
    del bpy.types.NodeSocket.show
