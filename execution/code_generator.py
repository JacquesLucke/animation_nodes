import os
from collections import defaultdict
from .. preferences import addonName, generateCompactCode


# Initial Socket Variables
##########################################

def getInitialVariables(nodes):
    variables = {}
    for node in nodes:
        for socket in node.sockets:
            variables[socket] = getSocketVariableName(socket)
    return variables

def getSocketVariableName(socket):
    socketID = socket.identifier if socket.identifier.isidentifier() else "_socket_{}_{}".format(socket.isOutput, socket.index)
    return "_{}{}".format(socketID, socket.node.identifier[:4])



# Setup Code
##########################################

def getSetupCode(nodes, variables):
    lines = []
    lines.append(get_ImportModules(nodes))
    lines.append(get_ImportAnimationNodes())
    lines.append(get_LoadRandomNumberCache())
    lines.extend(get_GetNodeReferences(nodes))
    lines.extend(get_GetSocketValues(nodes, variables))
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


def get_LoadRandomNumberCache():
    return "random_number_cache = animation_nodes.algorithms.random.getRandomNumberCache()"


def get_GetNodeReferences(nodes):
    lines = []
    lines.append("nodes = bpy.data.node_groups[{}].nodes".format(repr(nodes[0].nodeTree.name)))
    for node in nodes:
        lines.append("{} = nodes[{}]".format(node.identifier, repr(node.name)))
    return lines


def get_GetSocketValues(nodes, variables):
    lines = []
    for node in nodes:
        for socket in node.unlinkedInputs:
            lines.append(getLoadSocketValueLine(socket, variables))
    return lines


def getLoadSocketValueLine(socket, variables):
    if socket.hasValueCode:
        return "{} = {}".format(variables[socket], socket.getValueCode())
    else:
        socketsName = "inputs" if socket.isInput else "outputs"
        return "{} = {}.{}[{}].getValue()".format(variables[socket], socket.node.identifier, socketsName, socket.index)



# Node Execution Code
##########################################

def getNodeExecutionLines(node, variables):
    lines = []
    if not generateCompactCode(): lines.extend(getNodeCommentLines(node))
    lines.extend(getInputCopyLines(node, variables))
    taggedLines = node.getTaggedExecutionCodeLines()
    lines.extend([replaceTaggedLine(line, node, variables) for line in taggedLines])
    return lines

def getNodeCommentLines(node):
    return ["\n", "# Node: {} - {}".format(repr(node.nodeTree.name), repr(node.name))]

def getInputCopyLines(node, variables):
    lines = []
    for socket in node.inputs:
        if socket.dataIsModified and socket.isCopyable and socket.isUnlinked:
            newName = variables[socket] + "_copy"
            if socket.hasValueCode: line = "{} = {}".format(newName, socket.getValueCode())
            else: line = getCopyLine(socket, newName, variables)
            lines.append(line)
            variables[socket] = newName
    return lines

def replaceTaggedLine(line, node, variables):
    line = replace_NumberSign_NodeReference(line, node)
    line = replace_PercentSign_InputSocketVariable(line, node, variables)
    line = replace_DollarSign_OutputSocketVariable(line, node, variables)
    return line

def replace_NumberSign_NodeReference(line, node):
    return line.replace("#self#", node.identifier)

def replace_PercentSign_InputSocketVariable(line, node, variables):
    nodeInputs = node.inputsByIdentifier
    for name, variable in node.inputVariables.items():
        line = line.replace("%{}%".format(variable), variables[nodeInputs[name]])
    return line

def replace_DollarSign_OutputSocketVariable(line, node, variables):
    nodeOutputs = node.outputsByIdentifier
    for name, variable in node.outputVariables.items():
        line = line.replace("${}$".format(variable), variables[nodeOutputs[name]])
    return line



# Modify Socket Variables
##########################################

def linkOutputSocketsToTargets(node, variables):
    resolveInnerLinks(node, variables)
    lines = []
    for socket in node.linkedOutputs:
        lines.extend(linkSocketToTargets(socket, variables))
    return lines

def resolveInnerLinks(node, variables):
    inputs, outputs = node.inputsByIdentifier, node.outputsByIdentifier
    for inputName, outputName in node.innerLinks:
        variables[outputs[outputName]] = variables[inputs[inputName]]

def linkSocketToTargets(socket, variables):
    lines = []

    targets = socket.dataTargets
    needACopy = getTargetsThatNeedACopy(socket, targets)

    for target in socket.dataTargets:
        if target in needACopy:
            lines.append(getCopyLine(socket, variables[target], variables))
        else:
            variables[target] = variables[socket]

    return lines

def getTargetsThatNeedACopy(socket, targets):
    if not socket.isCopyable: return []
    modifiedTargets = [target for target in targets if target.dataIsModified]
    if socket.loop.copyAlways: return modifiedTargets
    if len(targets) == 1: return []
    if len(targets) > len(modifiedTargets): return modifiedTargets
    else: return modifiedTargets[1:]

def getCopyLine(fromSocket, targetName, variables):
    copyStatement = fromSocket.getCopyStatement().replace("value", variables[fromSocket])
    copyCode = "{} = {}".format(targetName, copyStatement)
    return copyCode
