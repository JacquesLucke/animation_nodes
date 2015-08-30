import bpy
from bpy.props import *
from .. import tree_info
from .. utils.recursion import noRecursion
from .. events import treeChanged, executionCodeChanged
from .. utils.names import getRandomString, toVariableName
from .. operators.dynamic_operators import getInvokeFunctionOperator
from .. nodes.system.utils import updateSubprogramInvokerNodes

class SocketTextProperties(bpy.types.PropertyGroup):
    bl_idname = "an_SocketTextProperties"
    unique = BoolProperty(default = False)
    editable = BoolProperty(default = False)
    variable = BoolProperty(default = False)

class SocketDisplayProperties(bpy.types.PropertyGroup):
    bl_idname = "an_SocketDisplayProperties"
    text = BoolProperty(default = False)
    textInput = BoolProperty(default = False)
    moveOperators = BoolProperty(default = False)
    removeOperator = BoolProperty(default = False)

class SocketLoopProperties(bpy.types.PropertyGroup):
    bl_idname = "an_SocketLoopProperties"

    def socketLoopPropertyChanged(self, context):
        updateSubprogramInvokerNodes()
        executionCodeChanged()

    useAsInput = BoolProperty(default = False, update = socketLoopPropertyChanged)
    useAsOutput = BoolProperty(default = False, update = socketLoopPropertyChanged)
    copyAlways = BoolProperty(default = False, update = socketLoopPropertyChanged)

class AnimationNodeSocket:
    storable = True

    def textChanged(self, context):
        updateText(self)

    text = StringProperty(default = "custom name", update = textChanged)
    removeable = BoolProperty(default = False)
    moveable = BoolProperty(default = False)
    moveGroup = IntProperty(default = 0)

    display = PointerProperty(type = SocketDisplayProperties)
    textProps = PointerProperty(type = SocketTextProperties)
    loop = PointerProperty(type = SocketLoopProperties)

    dataIsModified = BoolProperty(default = False)
    defaultDrawType = StringProperty(default = "TEXT_PROPERTY")

    def draw(self, context, layout, node, text):
        displayText = self.getDisplayedName()

        row = layout.row(align = True)
        if self.textProps.editable and self.display.textInput:
            row.prop(self, "text", text = "")
        else:
            if self.isInput and self.isUnlinked:
                self.drawSocket(row, displayText, self.defaultDrawType)
            else:
                if self.isOutput: row.alignment = "RIGHT"
                row.label(displayText)

        if self.moveable and self.display.moveOperators:
            row.separator()
            self.invokeFunction(row, "moveUpInGroup", icon = "TRIA_UP")
            self.invokeFunction(row, "moveDownInGroup", icon = "TRIA_DOWN")

        if self.removeable and self.display.removeOperator:
            row.separator()
            self.invokeFunction(row, "remove", icon = "X")

    def drawSocket(self, layout, text, drawType = "TEXT_PROPERTY"):
        '''
        Draw Types:
            TEXT_PROPERTY_OR_NONE: Draw only if a property exists
            TEXT_PROPERTY: Draw the text and the property if one exists
            PREFER_PROPERTY: Uses PROPERTY_ONLY is one exists, otherwise TEXT_ONLY
            PROPERTY_ONLY: Draw the property; If there is now property, draw nothing
            TEXT_ONLY: Ignore the property; Just label the text
        '''
        if drawType == "TEXT_PROPERTY_OR_NONE":
            if self.hasProperty: drawType = "TEXT_PROPERTY"

        if drawType == "PREFER_PROPERTY":
            if self.hasProperty: drawType = "PROPERTY_ONLY"
            else: drawType = "TEXT_ONLY"

        if drawType == "TEXT_PROPERTY":
            if self.hasProperty: self.drawProperty(layout, text)
            else: layout.label(text)
        elif drawType == "PROPERTY_ONLY":
            if self.hasProperty: self.drawProperty(layout, text = "")
        elif drawType == "TEXT_ONLY":
            layout.label(text)

    def getDisplayedName(self):
        if self.display.text or (self.textProps.editable and self.display.textInput):
            return self.text
        return self.name

    def toString(self):
        return self.getDisplayedName()

    def draw_color(self, context, node):
        return self.drawColor

    def getValue(self):
        return None

    def copyDisplaySettingsFrom(self, other):
        self.display.text = other.display.text
        self.display.textInput = other.display.textInput
        self.display.moveOperators = other.display.moveOperators
        self.display.removeOperator = other.display.removeOperator

    def setProperty(self, data):
        pass

    def getProperty(self):
        return

    def invokeFunction(self, layout, functionName, text = "", icon = "NONE", description = "", emboss = True, data = None):
        idName = getInvokeFunctionOperator(description)
        props = layout.operator(idName, text = text, icon = icon, emboss = emboss)
        props.classType = "SOCKET"
        props.treeName = self.nodeTree.name
        props.nodeName = self.node.name
        props.isOutput = self.isOutput
        props.identifier = self.identifier
        props.functionName = functionName
        props.invokeWithData = data is not None
        props.data = str(data)

    def moveUp(self):
        self.moveTo(self.index - 1)

    def moveTo(self, index):
        if self.index != index:
            self.sockets.move(self.index, index)
            self.node.socketMoved()

    def moveUpInGroup(self):
        """Cares about moveable sockets"""
        self.moveInGroup(moveUp = True)

    def moveDownInGroup(self):
        """Cares about moveable sockets"""
        self.moveInGroup(moveUp = False)

    def moveInGroup(self, moveUp = True):
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

    def removeLinks(self):
        tree = self.nodeTree
        for link in self.links:
            tree.links.remove(link)

    def disableSocketEditingInNode(self):
        self.display.textInput = False
        self.display.moveOperators = False
        self.display.removeOperator = False

    @property
    def isOutput(self):
        return self.is_output

    @property
    def isInput(self):
        return not self.is_output

    @property
    def nodeTree(self):
        return self.node.id_data

    @property
    def index(self):
        return list(self.sockets).index(self)

    @property
    def sockets(self):
        """Returns all sockets next to this one (all inputs or outputs)"""
        return self.node.outputs if self.isOutput else self.node.inputs

    @property
    def isLinked(self):
        return tree_info.isSocketLinked(self)

    @property
    def isUnlinked(self):
        return not self.isLinked


    @property
    def dataOrigin(self):
        sockets = self.linkedSockets
        if len(sockets) > 0: return sockets[0]

    @property
    def directOrigin(self):
        sockets = self.directlyLinkedSockets
        if len(sockets) > 0: return sockets[0]

    @property
    def dataTargets(self):
        return self.linkedSockets

    @property
    def directTargets(self):
        return self.directlyLinkedSockets

    @property
    def linkedNodes(self):
        nodes = [socket.node for socket in self.linkedSockets]
        return list(set(nodes))

    @property
    def directlyLinkedNodes(self):
        nodes = [socket.node for socket in self.directlyLinkedSockets]
        return list(set(nodes))


    @property
    def linkedSockets(self):
        return tree_info.getLinkedSockets(self)

    @property
    def directlyLinkedSockets(self):
        return tree_info.getDirectlyLinkedSockets(self)


    @property
    def isCopyable(self):
        return hasattr(self, "getCopyStatement")

    @property
    def hasValueCode(self):
        return hasattr(self, "getValueCode")

    @property
    def hasProperty(self):
        return hasattr(self, "drawProperty")



@noRecursion
def updateText(socket):
    correctText(socket)

def correctText(socket):
    if socket.textProps.variable:
        socket.text = toVariableName(socket.text)
    if socket.textProps.unique:
        text = socket.text
        socket.text = "temporary name to avoid some errors"
        socket.text = getNotUsedText(socket.node, prefix = text)
    socket.node.customSocketNameChanged(socket)

def getNotUsedText(node, prefix):
    text = prefix
    while isTextUsed(node, text):
        text = prefix + "_" + getRandomString(2)
    return text

def isTextUsed(node, name):
    for socket in node.sockets:
        if socket.text == name: return True
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
