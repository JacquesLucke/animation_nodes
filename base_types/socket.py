import bpy
from bpy.props import *
from .. events import treeChanged, executionCodeChanged
from .. utils.recursion import noRecursion
from .. utils.names import getRandomString, toVariableName
from .. tree_info import isSocketLinked, getOriginSocket, getDirectOriginSocket, getTargetSockets, getLinkedSockets
from . socket_function_call import getSocketFunctionCallOperatorName

class CustomNameProperties(bpy.types.PropertyGroup):
    bl_idname = "an_CustomNameProperties"
    unique = BoolProperty(default = False)
    editable = BoolProperty(default = False)
    variable = BoolProperty(default = False)

class SocketEditDisplayProperties(bpy.types.PropertyGroup):
    bl_idname = "an_SocketEditDisplayProperties"
    customNameInput = BoolProperty(default = False)
    moveOperators = BoolProperty(default = False)
    removeOperator = BoolProperty(default = False)

class AnimationNodeSocket:

    def customNameChanged(self, context):
        updateCustomName(self)

    customName = StringProperty(default = "custom name", update = customNameChanged)
    displayCustomName = BoolProperty(default = False)
    nameSettings = PointerProperty(type = CustomNameProperties)
    display = PointerProperty(type = SocketEditDisplayProperties)

    removeable = BoolProperty(default = False)
    moveGroup = IntProperty(default = 0)
    moveable = BoolProperty(default = False)

    dataIsModified = BoolProperty(default = False)
    copyAlways = BoolProperty(default = False, update = executionCodeChanged)

    def draw(self, context, layout, node, text):
        displayText = self.getDisplayedName()

        row = layout.row(align = True)
        if self.nameSettings.editable and self.display.customNameInput:
            row.prop(self, "customName", text = "")
        else:
            if not self.is_output and not self.isLinked:
                self.drawInput(row, node, displayText)
            else:
                if self.is_output: row.alignment = "RIGHT"
                row.label(displayText)

        if self.moveable and self.display.moveOperators:
            row.separator()
            self.functionOperator(row, "moveUpSave", icon = "TRIA_UP")
            self.functionOperator(row, "moveDownSave", icon = "TRIA_DOWN")

        if self.removeable and self.display.removeOperator:
            row.separator()
            self.functionOperator(row, "remove", icon = "X")

    def getDisplayedName(self):
        if self.displayCustomName or (self.nameSettings.editable and self.display.customNameInput):
            return self.customName
        return self.name

    def toString(self):
        return self.getDisplayedName()

    def draw_color(self, context, node):
        return self.drawColor

    def getValue(self):
        return None

    def copyDisplaySettingsFrom(self, other):
        self.displayCustomName = other.displayCustomName
        self.display.customNameInput = other.display.customNameInput
        self.display.moveOperators = other.display.moveOperators
        self.display.removeOperator = other.display.removeOperator

    def setStoreableValue(self, data):
        pass

    def getStoreableValue(self):
        return

    def functionOperator(self, layout, functionName, text = "", icon = "NONE", description = "", emboss = True):
        idName = getSocketFunctionCallOperatorName(description)
        props = layout.operator(idName, text = text, icon = icon, emboss = emboss)
        props.nodeTreeName = self.node.id_data.name
        props.nodeName = self.node.name
        props.isOutput = self.is_output
        props.identifier = self.identifier
        props.functionName = functionName

    def moveUp(self):
        self.moveTo(self.index - 1)

    def moveTo(self, index):
        if self.index != index:
            self.sockets.move(self.index, index)
            self.node.socketMoved()

    def moveUpSave(self):
        """Cares about moveable sockets"""
        self.moveSave(moveUp = True)

    def moveDownSave(self):
        """Cares about moveable sockets"""
        self.moveSave(moveUp = False)

    def moveSave(self, moveUp = True):
        """Cares about moveable sockets"""
        if not self.moveable: return
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
            self.node.socketMoved()

    def remove(self):
        node = self.node
        node.removeSocket(self)
        node.socketRemoved()

    def linkWith(self, socket):
        if self.isOutput: self.nodeTree.links.new(socket, self)
        else: self.nodeTree.links.new(self, socket)

    def removeConnectedLinks(self):
        tree = self.node.id_data
        for link in self.links:
            tree.links.remove(link)

    def disableSocketEditingInNode(self):
        self.display.customNameInput = False
        self.display.moveOperators = False
        self.display.removeOperator = False

    @property
    def isOutput(self):
        return self.is_output

    @property
    def nodeTree(self):
        return self.node.id_data

    @property
    def index(self):
        return list(self.sockets).index(self)

    @property
    def sockets(self):
        """Returns all sockets next to this one (all inputs or outputs)"""
        return self.node.outputs if self.is_output else self.node.inputs

    @property
    def isLinked(self):
        return isSocketLinked(self)

    @property
    def isUnlinked(self):
        return not self.isLinked

    @property
    def linkedNodes(self):
        nodes = [socket.node for socket in self.linkedDataSockets]
        return list(set(nodes))

    @property
    def linkedDataSockets(self):
        return getLinkedSockets(self)

    @property
    def dataOriginSocket(self):
        return getOriginSocket(self)

    @property
    def dataTargetSockets(self):
        return getTargetSockets(self)

    @property
    def directOriginSocket(self):
        return getDirectOriginSocket(self)

    @property
    def isCopyable(self):
        return hasattr(self, "getCopyStatement")

    @property
    def hasValueCode(self):
        return hasattr(self, "getValueCode")



@noRecursion
def updateCustomName(socket):
    correctCustomName(socket)

def correctCustomName(socket):
    if socket.nameSettings.variable:
        socket.customName = toVariableName(socket.customName)
    if socket.nameSettings.unique:
        customName = socket.customName
        socket.customName = "temporary name to avoid some errors"
        socket.customName = getNotUsedCustomName(socket.node, prefix = customName)
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
