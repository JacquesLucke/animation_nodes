import os
from collections import defaultdict
from .. preferences import addonName


# Initial Socket Variables
##########################################

def getInitialSocketVariables(nodes):
    socketVariables = {}
    for node in nodes:
        for socket in node.sockets:
            socketVariables[socket] = getSocketVariableName(socket)
    return socketVariables

def getSocketVariableName(socket):
    socketID = socket.identifier if socket.identifier.isidentifier() else "_socket_{}_{}".format(socket.isOutput, socket.index)
    return "_{}{}".format(socketID, socket.node.identifier[:4])



# Setup Code
##########################################

def getSetupCode(nodes, socketVariables):
    lines = []
    lines.append(get_ImportModules(nodes))
    lines.append(get_ImportAnimationNodes())
    lines.extend(get_GetNodeReferences(nodes))
    lines.extend(get_GetSocketValues(nodes, socketVariables))
    return "\n".join(lines)


def get_ImportModules(nodes):
    neededModules = {"bpy", "sys"}
    neededModules.update(getModulesNeededByNodes(nodes))
    modulesString = ", ".join(neededModules)
    return "import " + modulesString

def getModulesNeededByNodes(nodes):
    moduleNames = set()
    for node in nodes:
        moduleNames.update(node.getModuleList())
    return list(moduleNames)


def get_ImportAnimationNodes():
    '''
    This needs a special import because the module name can be
    different because the package folder has another name.
    Github extends the name with '-master'
    '''
    return "animation_nodes = sys.modules.get({})".format(repr(addonName))


def get_GetNodeReferences(nodes):
    lines = []
    lines.append("nodes = bpy.data.node_groups[{}].nodes".format(repr(nodes[0].nodeTree.name)))
    for node in nodes:
        lines.append("{} = nodes[{}]".format(node.identifier, repr(node.name)))
    return lines


def get_GetSocketValues(nodes, socketVariables):
    lines = []
    for node in nodes:
        for socket in node.unlinkedInputs:
            lines.append("{} = {}.inputs[{}].getValue()".format(
                socketVariables[socket], node.identifier, socket.index))
    return lines



# Node Execution Code
##########################################

def getNodeExecutionLines(node, socketVariables):
    lines = ["\n", "# Node: {} - {}".format(repr(node.nodeTree.name), repr(node.name))]
    lines.extend(getInputCopyLines(node, socketVariables))
    taggedLines = node.getTaggedExecutionCodeLines()
    lines.extend([replaceTaggedLine(line, node, socketVariables) for line in taggedLines])
    return lines

def getInputCopyLines(node, socketVariables):
    lines = []
    for socket in node.inputs:
        if socket.dataIsModified and socket.isCopyable and socket.isUnlinked:
            newName = socketVariables[socket] + "_copy"
            lines.append(getCopyLine(socket, newName, socketVariables))
            socketVariables[socket] = newName
    return lines

def replaceTaggedLine(line, node, socketVariables):
    line = replace_NumberSign_NodeReference(line, node)
    line = replace_PercentSign_InputSocketVariable(line, node, socketVariables)
    line = replace_DollarSign_OutputSocketVariable(line, node, socketVariables)
    return line

def replace_NumberSign_NodeReference(line, node):
    return line.replace("#self#", node.identifier)

def replace_PercentSign_InputSocketVariable(line, node, socketVariables):
    nodeInputs = node.inputsByIdentifier
    for name, identifier in node.inputNames.items():
        line = line.replace("%{}%".format(identifier), socketVariables[nodeInputs[name]])
    return line

def replace_DollarSign_OutputSocketVariable(line, node, socketVariables):
    nodeOutputs = node.outputsByIdentifier
    for name, identifier in node.outputNames.items():
        line = line.replace("${}$".format(identifier), socketVariables[nodeOutputs[name]])
    return line



# Modify Socket Variables
##########################################

def linkOutputSocketsToTargets(node, socketVariables):
    resolveInnerLinks(node, socketVariables)
    lines = []
    for socket in node.linkedOutputs:
        lines.extend(linkSocketToTargets(socket, socketVariables))
    return lines

def resolveInnerLinks(node, socketVariables):
    inputs, outputs = node.inputsByIdentifier, node.outputsByIdentifier
    for inputName, outputName in node.innerLinks:
        socketVariables[outputs[outputName]] = socketVariables[inputs[inputName]]

def linkSocketToTargets(socket, socketVariables):
    lines = []

    targets = socket.dataTargetSockets
    needACopy = getTargetsThatNeedACopy(socket, targets)

    for target in socket.dataTargetSockets:
        if target in needACopy:
            lines.append(getCopyLine(socket, socketVariables[target], socketVariables))
        else:
            socketVariables[target] = socketVariables[socket]

    return lines

def getTargetsThatNeedACopy(socket, targets):
    if not socket.isCopyable: return []
    modifiedTargets = [target for target in targets if target.dataIsModified]
    if socket.copyAlways: return modifiedTargets
    if len(targets) == 1: return []
    if len(targets) > len(modifiedTargets): return modifiedTargets
    else: return modifiedTargets[1:]

def getCopyLine(fromSocket, targetName, socketVariables):
    copyStatement = fromSocket.getCopyStatement().replace("value", socketVariables[fromSocket])
    copyCode = "{} = {}".format(targetName, copyStatement)
    return copyCode
