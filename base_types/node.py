import re
import bpy
import types
import random
from bpy.props import *
from collections import defaultdict
from .. utils.handlers import eventHandler
from .. ui.node_colors import colorNetworks
from .. utils.nodes import getAnimationNodeTrees
from .. operators.callbacks import newNodeCallback
from .. sockets.info import toIdName as toSocketIdName
from .. utils.blender_ui import iterNodeCornerLocations
from .. operators.dynamic_operators import getInvokeFunctionOperator
from .. tree_info import (getNetworkWithNode, getDirectlyLinkedSockets, getOriginNodes,
                          getLinkedInputsDict, getLinkedOutputsDict, iterLinkedOutputSockets,
                          iterUnlinkedInputSockets)

class AnimationNode:
    bl_width_max = 5000
    _isAnimationNode = True

    def useNetworkColorChanged(self, context):
        colorNetworks()

    # unique string for each node; don't change it at all
    identifier = StringProperty(name = "Identifier", default = "")
    inInvalidNetwork = BoolProperty(name = "In Invalid Network", default = False)
    useNetworkColor = BoolProperty(name = "Use Network Color", default = True, update = useNetworkColorChanged)

    # used for the listboxes in the sidebar
    activeInputIndex = IntProperty()
    activeOutputIndex = IntProperty()

    searchTags = []
    onlySearchTags = False
    # can contain: 'No Execution', 'No Subprogram', 'No Auto Execution'
    options = set()

    # can be "NONE", "ALWAYS" or "HIDDEN_ONLY"
    dynamicLabelType = "NONE"

    @classmethod
    def poll(cls, nodeTree):
        return nodeTree.bl_idname == "an_AnimationNodeTree"


    # functions subclasses can override
    ######################################

    def create(self):
        pass

    def edit(self):
        pass

    def duplicate(self, sourceNode):
        pass

    def delete(self):
        pass

    def draw(self, layout):
        pass

    def drawLabel(self):
        return self.bl_label

    def drawAdvanced(self, layout):
        layout.label("Has no advanced settings")

    def socketRemoved(self):
        self.socketChanged()

    def socketMoved(self):
        self.socketChanged()

    def customSocketNameChanged(self, socket):
        self.socketChanged()

    def socketChanged(self):
        """
        Use this function when you don't need
        to know what happened exactly to the sockets
        """
        pass

    def getExecutionCode(self):
        return []

    def getUsedModules(self):
        return []

    def drawControlSocket(self, layout, socket):
        layout.alignment = "LEFT" if socket.isInput else "RIGHT"
        layout.label(socket.name)

    @classmethod
    def getSearchTags(cls):
        return cls.searchTags

    def getTemplateCode(self):
        return []

    # Don't override these functions
    ######################################

    def init(self, context):
        self.width_hidden = 100
        self.identifier = createIdentifier()
        self.create()

    def update(self):
        '''Don't use this function at all!!'''
        pass

    def copy(self, sourceNode):
        self.identifier = createIdentifier()
        self.duplicate(sourceNode)

    def free(self):
        self.delete()

    def draw_buttons(self, context, layout):
        if self.inInvalidNetwork: layout.label("Invalid Network", icon = "ERROR")
        if self.nodeTree.editNodeLabels: layout.prop(self, "label", text = "")
        self.draw(layout)

    def draw_label(self):
        if self.dynamicLabelType == "NONE":
            return self.bl_label
        elif self.dynamicLabelType == "ALWAYS":
            return self.drawLabel()
        elif self.dynamicLabelType == "HIDDEN_ONLY" and self.hide:
            return self.drawLabel()
        else:
            return self.bl_label

    def newInput(self, type, name, identifier = None, **kwargs):
        idName = toSocketIdName(type)
        if identifier is None: identifier = name
        socket = self.inputs.new(idName, name, identifier)
        self._setSocketProperties(socket, kwargs)
        return socket

    def newOutput(self, type, name, identifier = None, **kwargs):
        idName = toSocketIdName(type)
        if identifier is None: identifier = name
        socket = self.outputs.new(idName, name, identifier)
        self._setSocketProperties(socket, kwargs)
        return socket

    def _setSocketProperties(self, socket, properties):
        for key, value in properties.items():
            setattr(socket, key, value)

    def invokeFunction(self, layout, functionName, text = "", icon = "NONE", description = "", emboss = True, confirm = False, data = None, passEvent = False):
        idName = getInvokeFunctionOperator(description)
        props = layout.operator(idName, text = text, icon = icon, emboss = emboss)
        props.callback = self.newCallback(functionName)
        props.invokeWithData = data is not None
        props.confirm = confirm
        props.data = str(data)
        props.passEvent = passEvent

    def invokeSocketTypeChooser(self, layout, functionName, socketGroup = "ALL", text = "", icon = "NONE", description = "", emboss = True):
        data = functionName + "," + socketGroup
        self.invokeFunction(layout, "_chooseSocketDataType", text = text, icon = icon, description = description, emboss = emboss, data = data)

    def _chooseSocketDataType(self, data):
        functionName, socketGroup = data.split(",")
        bpy.ops.an.choose_socket_type("INVOKE_DEFAULT",
            socketGroup = socketGroup,
            callback = self.newCallback(functionName))

    def invokePathChooser(self, layout, functionName, text = "", icon = "NONE", description = "", emboss = True):
        data = functionName
        self.invokeFunction(layout, "_choosePath", text = text, icon = icon, description = description, emboss = emboss, data = data)

    def _choosePath(self, data):
        bpy.ops.an.choose_path("INVOKE_DEFAULT",
            callback = self.newCallback(data))

    def invokeIDKeyChooser(self, layout, functionName, text = "", icon = "NONE", description = "", emboss = True):
        data = functionName
        self.invokeFunction(layout, "_chooseIDKeys", text = text, icon = icon, description = description, emboss = emboss, data = data)

    def _chooseIDKeys(self, data):
        bpy.ops.an.choose_id_key("INVOKE_DEFAULT",
            callback = self.newCallback(data))

    def invokePopup(self, layout, drawFunctionName, executeFunctionName = "", text = "", icon = "NONE", description = "", emboss = True, width = 250):
        data = drawFunctionName + "," + executeFunctionName + "," + str(width)
        self.invokeFunction(layout, "_openNodePopup", text = text, icon = icon, description = description, emboss = emboss, data = data)

    def _openNodePopup(self, data):
        drawFunctionName, executeFunctionName, width = data.split(",")
        bpy.ops.an.node_popup("INVOKE_DEFAULT",
            nodeIdentifier = self.identifier,
            drawFunctionName = drawFunctionName,
            executeFunctionName = executeFunctionName,
            width = int(width))

    def invokeAreaChooser(self, layout, functionName, text = "", icon = "NONE", description = "", emboss = True):
        data = functionName
        self.invokeFunction(layout, "_chooseArea", text = text, icon = icon, description = description, emboss = emboss, data = data)

    def _chooseArea(self, data):
        bpy.ops.an.select_area("INVOKE_DEFAULT",
            callback = self.newCallback(data))

    def newCallback(self, functionName):
        return newNodeCallback(self, functionName)

    def clearSockets(self):
        self.inputs.clear()
        self.outputs.clear()

    def removeSocket(self, socket):
        index = socket.getIndex()
        if socket.isOutput:
            if index < self.activeOutputIndex: self.activeOutputIndex -= 1
        else:
            if index < self.activeInputIndex: self.activeInputIndex -= 1
        socket.sockets.remove(socket)

    def remove(self):
        self.nodeTree.nodes.remove(self)


    def getLinkedInputsDict(self):
        return getLinkedInputsDict(self)

    def getLinkedOutputsDict(self):
        return getLinkedOutputsDict(self)


    def getVisibleInputs(self):
        return [socket for socket in self.inputs if not socket.hide]

    def getVisibleOutputs(self):
        return [socket for socket in self.outputs if not socket.hide]


    def disableSocketEditingInNode(self):
        for socket in self.sockets:
            socket.disableSocketEditingInNode()

    def toggleTextInputVisibility(self):
        self.toggleSocketDisplayProperty("textInput")

    def toggleMoveOperatorsVisibility(self):
        self.toggleSocketDisplayProperty("moveOperators")

    def toggleRemoveOperatorVisibility(self):
        self.toggleSocketDisplayProperty("removeOperator")

    def toggleSocketDisplayProperty(self, name):
        if len(self.sockets) == 0: return
        state = not getattr(self.sockets[0].display, name)
        for socket in self.sockets:
            setattr(socket.display, name, state)


    def getNodesWhenFollowingLinks(self, followInputs = False, followOutputs = False):
        nodes = set()
        nodesToCheck = {self}
        while nodesToCheck:
            node = nodesToCheck.pop()
            nodes.add(node)
            sockets = []
            if followInputs: sockets.extend(node.inputs)
            if followOutputs: sockets.extend(node.outputs)
            for socket in sockets:
                # cannot use a socket function because there are reroutes etc
                for linkedSocket in getDirectlyLinkedSockets(socket):
                    node = linkedSocket.node
                    if node not in nodes: nodesToCheck.add(node)
        nodes.remove(self)
        return list(nodes)

    def removeLinks(self):
        removedLink = False
        for socket in self.sockets:
            if socket.removeLinks():
                removedLink = True
        return removedLink


    @property
    def nodeTree(self):
        return self.id_data

    @property
    def inputsByIdentifier(self):
        return {socket.identifier : socket for socket in self.inputs}

    @property
    def outputsByIdentifier(self):
        return {socket.identifier : socket for socket in self.outputs}

    @property
    def inputsByText(self):
        return {socket.text : socket for socket in self.inputs}

    @property
    def linkedOutputs(self):
        return tuple(iterLinkedOutputSockets(self))

    @property
    def activeInputSocket(self):
        if len(self.inputs) == 0: return None
        return self.inputs[self.activeInputIndex]

    @property
    def activeOutputSocket(self):
        if len(self.outputs) == 0: return None
        return self.outputs[self.activeOutputIndex]

    @property
    def originNodes(self):
        return getOriginNodes(self)

    @property
    def unlinkedInputs(self):
        return tuple(iterUnlinkedInputSockets(self))

    @property
    def network(self):
        return getNetworkWithNode(self)

    @property
    def sockets(self):
        return list(self.inputs) + list(self.outputs)

    @property
    def inputVariables(self):
        return {socket.identifier : socket.identifier for socket in self.inputs}

    @property
    def outputVariables(self):
        return {socket.identifier : socket.identifier for socket in self.outputs}

    def iterInnerLinks(self):
        names = {}
        for identifier, variable in self.inputVariables.items():
            names[variable] = identifier
        for identifier, variable in self.outputVariables.items():
            if variable in names:
                yield (names[variable], identifier)

    def getTemplateCodeString(self):
        return toString(self.getTemplateCode())

    def getLocalExecutionCode(self):
        inputVariables = self.inputVariables
        outputVariables = self.outputVariables

        if hasattr(self, "execute"):
            return self.getLocalExecutionCode_ExecuteFunction(inputVariables, outputVariables)
        else:
            return self.getLocalExecutionCode_GetExecutionCode(inputVariables, outputVariables)

    def getLocalExecutionCode_ExecuteFunction(self, inputVariables, outputVariables):
        parameterString = ", ".join(inputVariables[socket.identifier] for socket in self.inputs)
        executionString = "self.execute({})".format(parameterString)

        outputString = ", ".join(outputVariables[socket.identifier] for socket in self.outputs)

        if outputString == "": return executionString
        else: return "{} = {}".format(outputString, executionString)

    def getLocalExecutionCode_GetExecutionCode(self, inputVariables, outputVariables):
        return toString(self.getExecutionCode())


@eventHandler("SCENE_UPDATE_POST")
def createMissingIdentifiers(scene = None):
    def unidentifiedNodes():
        for tree in getAnimationNodeTrees():
            for node in tree.nodes:
                if not issubclass(type(node), AnimationNode): continue
                if node.identifier == "": yield node

    for node in unidentifiedNodes():
        node.identifier = createIdentifier()

def createIdentifier():
    identifierLength = 15
    characters = "abcdefghijklmnopqrstuvwxyz" + "0123456789"
    choice = random.SystemRandom().choice
    return "_" + ''.join(choice(characters) for _ in range(identifierLength))

def toString(code):
    if isinstance(code, types.GeneratorType):
        code = list(code)
    if isinstance(code, (list, tuple)):
        return "\n".join(code)
    return code



# Register
##################################

def nodeToID(node):
    return (node.id_data.name, node.name)

def isAnimationNode(node):
    return hasattr(node, "_isAnimationNode")

def getNodeTree(node):
    return node.id_data

def getViewLocation(node):
    location = node.location.copy()
    while node.parent:
        node = node.parent
        location += node.location.copy()
    return location

def getRegionBottomLeft(node, region):
    return next(iterNodeCornerLocations([node], region, horizontal = "LEFT"))

def getRegionBottomRight(node, region):
    return next(iterNodeCornerLocations([node], region, horizontal = "RIGHT"))

def register():
    bpy.types.Node.toID = nodeToID
    bpy.types.Node.isAnimationNode = BoolProperty(name = "Is Animation Node", get = isAnimationNode)
    bpy.types.Node.viewLocation = FloatVectorProperty(name = "Region Location", size = 2, subtype = "XYZ", get = getViewLocation)
    bpy.types.Node.getNodeTree = getNodeTree
    bpy.types.Node.getRegionBottomLeft = getRegionBottomLeft
    bpy.types.Node.getRegionBottomRight = getRegionBottomRight

def unregister():
    pass
