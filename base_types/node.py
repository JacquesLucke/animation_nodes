import re
import bpy
import types
import random
from bpy.props import *
from collections import defaultdict
from bpy.app.handlers import persistent
from .. ui.node_colors import colorNetworks
from .. utils.nodes import getAnimationNodeTrees
from .. operators.dynamic_operators import getInvokeFunctionOperator
from .. tree_info import getNetworkWithNode, getDirectlyLinkedSockets, getOriginNodes

class AnimationNode:
    isAnimationNode = True

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

    def invokeFunction(self, layout, functionName, text = "", icon = "NONE", description = "", emboss = True, data = None):
        idName = getInvokeFunctionOperator(description)
        props = layout.operator(idName, text = text, icon = icon, emboss = emboss)
        props.classType = "NODE"
        props.treeName = self.nodeTree.name
        props.nodeName = self.name
        props.functionName = functionName
        props.invokeWithData = data is not None
        props.data = str(data)

    def invokeSocketTypeChooser(self, layout, functionName, socketGroup = "ALL", text = "", icon = "NONE", description = "", emboss = True):
        data = functionName + "," + socketGroup
        self.invokeFunction(layout, "_chooseSocketDataType", text = text, icon = icon, description = description, emboss = emboss, data = data)

    def _chooseSocketDataType(self, data):
        callback, socketGroup = data.split(",")
        bpy.ops.an.choose_socket_type("INVOKE_DEFAULT",
            nodeIdentifier = self.identifier,
            socketGroup = socketGroup,
            callback = callback)

    def invokePathChooser(self, layout, functionName, text = "", icon = "NONE", description = "", emboss = True):
        data = functionName
        self.invokeFunction(layout, "_choosePath", text = text, icon = icon, description = description, emboss = emboss, data = data)

    def _choosePath(self, data):
        bpy.ops.an.choose_path("INVOKE_DEFAULT",
            nodeIdentifier = self.identifier,
            callback = data)

    def clearSockets(self):
        self.inputs.clear()
        self.outputs.clear()

    def removeSocket(self, socket):
        index = socket.index
        if socket.isOutput:
            if index < self.activeOutputIndex: self.activeOutputIndex -= 1
        else:
            if index < self.activeInputIndex: self.activeInputIndex -= 1
        socket.sockets.remove(socket)


    def getLinkedInputsDict(self):
        linkedInputs = {socket.identifier : socket.isLinked for socket in self.inputs}
        return linkedInputs

    def getLinkedOutputsDict(self):
        linkedOutputs = {socket.identifier : socket.isLinked for socket in self.outputs}
        return linkedOutputs


    def disableSocketEditingInNode(self):
        for socket in self.sockets:
            socket.disableSocketEditingInNode()

    def toogleTextInputVisibility(self):
        self.toogleSocketDisplayProperty("textInput")

    def toogleMoveOperatorsVisibility(self):
        self.toogleSocketDisplayProperty("moveOperators")

    def toogleRemoveOperatorVisibility(self):
        self.toogleSocketDisplayProperty("removeOperator")

    def toogleSocketDisplayProperty(self, name):
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
        return [socket for socket in self.outputs if socket.isLinked]

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
        return [socket for socket in self.inputs if not socket.isLinked]

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

    @property
    def innerLinks(self):
        names = defaultdict(list)
        for identifier, variable in self.inputVariables.items():
            names[variable].append(identifier)
        for identifier, variable in self.outputVariables.items():
            names[variable].append(identifier)

        links = []
        for name, identifiers in names.items():
            if len(identifiers) == 2: links.append(identifiers)
        return links

    def getTemplateCodeString(self):
        return toString(self.getTemplateCode())

    def getExecutionCodeString(self):
        return toString(self.getExecutionCode())

    def getTaggedExecutionCodeLines(self):
        """
        tags:
            # - self
            % - input variables
            $ - output variables
        """
        inputVariables = self.inputVariables
        outputVariables = self.outputVariables

        if hasattr(self, "execute"):
            parameters = ["%{0}%".format(inputVariables[socket.identifier]) for socket in self.inputs]
            parameterString = ", ".join(parameters)

            executionString = "#self#.execute(" + parameterString + ")"

            outputVariables = ["${}$".format(outputVariables[socket.identifier]) for socket in self.outputs]
            outputString = ", ".join(outputVariables)

            if outputString == "": return [executionString]
            return [outputString + " = "+ executionString]
        else:
            code = toString(self.getExecutionCode())
            for variable in inputVariables.values():
                code = tagVariableName(code, variable, "%")
            for variable in outputVariables.values():
                code = tagVariableName(code, variable, "$")
            code = tagVariableName(code, "self", "#")
            return code.split("\n")

from functools import lru_cache
@lru_cache(maxsize = 2048)
def tagVariableName(code, name, tag):
    """
    Find all occurences of 'name' in 'code' and set 'tag' before and after it.
    The occurence must not have a dot before it.
    """
    code = re.sub(r"([^\.\"\%']|^)\b({})\b".format(name), r"\1{0}\2{0}".format(tag), code)
    return code

@persistent
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

def nodeToID(self):
    return (self.id_data.name, self.name)

def registerHandlers():
    bpy.types.Node.toID = nodeToID
    bpy.app.handlers.load_post.append(createMissingIdentifiers)

def unregisterHandlers():
    bpy.app.handlers.load_post.remove(createMissingIdentifiers)
