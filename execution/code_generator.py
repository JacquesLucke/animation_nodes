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
    lines = node.getTaggedExecutionCodeLines()
    lines = [replaceTaggedLine(line, node, socketVariables) for line in lines]
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
    for socket in node.linkedOutputs:
        linkSocketToTargets(socket, socketVariables)

def linkSocketToTargets(socket, socketVariables):
    for target in socket.dataTargetSockets:
        socketVariables[target] = socketVariables[socket]
