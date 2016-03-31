import os
import traceback
from itertools import chain
from collections import defaultdict
from .. problems import NodeFailesToCreateExecutionCode
from .. preferences import addonName, monitoredExecutionIsEnabled


# Initial Socket Variables
##########################################

def getInitialVariables(nodes):
    variables = {}
    for node in nodes:
        for socket in chain(node.inputs, node.outputs):
            variables[socket] = getSocketVariableName(socket)
    return variables

def getSocketVariableName(socket):
    socketID = socket.identifier if socket.identifier.isidentifier() else "_socket_{}_{}".format(socket.isOutput, socket.index)
    return "_{}{}".format(socketID, socket.node.identifier[:4])



# Setup Code
##########################################

def iterSetupCodeLines(nodes, variables):
    yield get_ImportModules(nodes)
    yield get_ImportAnimationNodes()
    yield get_LoadRandomNumberCache()
    yield from iter_GetNodeReferences(nodes)
    yield from iter_GetSocketValues(nodes, variables)


def get_ImportModules(nodes):
    neededModules = {"bpy", "sys"}
    neededModules.update(getModulesNeededByNodes(nodes))
    modulesString = ", ".join(neededModules)
    return "import " + modulesString

def getModulesNeededByNodes(nodes):
    moduleNames = set()
    for node in nodes:
        moduleNames.update(node.getUsedModules())
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


def iter_GetNodeReferences(nodes):
    yield "nodes = bpy.data.node_groups[{}].nodes".format(repr(nodes[0].nodeTree.name))
    for node in nodes:
        yield "{} = nodes[{}]".format(node.identifier, repr(node.name))


def iter_GetSocketValues(nodes, variables):
    for socket in iterUnlinkedSockets(nodes):
        yield getLoadSocketValueLine(socket, variables)

def iterUnlinkedSockets(nodes):
    for node in nodes:
        yield from node.unlinkedInputs


def getLoadSocketValueLine(socket, variables):
    return "{} = {}".format(variables[socket], getSocketValueExpression(socket))

def getSocketValueExpression(socket):
    if socket.hasValueCode: return socket.getValueCode()
    else:
        socketsName = "inputs" if socket.isInput else "outputs"
        return "{}.{}[{}].getValue()".format(socket.node.identifier, socketsName, socket.index)



# Node Execution Code
##########################################

def getGlobalizeStatement(nodes, variables):
    socketNames = [variables[socket] for socket in iterUnlinkedSockets(nodes)]
    if len(socketNames) == 0: return ""
    return "global " + ", ".join(socketNames)

def getFunction_IterNodeExecutionLines():
    if monitoredExecutionIsEnabled():
        return iterNodeExecutionLines_Monitored
    else:
        return iterNodeExecutionLines_Basic

def iterNodeExecutionLines_Monitored(node, variables):
    yield from iterNodePreExecutionLines(node, variables)
    yield "try:"
    try:
        for line in iterRealNodeExecutionLines(node, variables):
            yield "    " + line
    except:
        handleExecutionCodeCreationException(node)
    yield "    pass"
    yield "except:"
    yield "    animation_nodes.problems.NodeRaisesExceptionDuringExecution({}).report()".format(repr(node.identifier))
    yield "    raise Exception()"

def iterNodeExecutionLines_Basic(node, variables):
    yield from iterNodePreExecutionLines(node, variables)
    try:
        yield from iterRealNodeExecutionLines(node, variables)
    except:
        handleExecutionCodeCreationException(node)

def iterNodePreExecutionLines(node, variables):
    yield ""
    yield getNodeCommentLine(node)
    yield from iterInputCopyLines(node, variables)

def getNodeCommentLine(node):
    return "# Node: {} - {}".format(repr(node.nodeTree.name), repr(node.name))

def iterInputCopyLines(node, variables):
    for socket in node.inputs:
        if socket.dataIsModified and socket.isCopyable and socket.isUnlinked:
            newName = variables[socket] + "_copy"
            if socket.hasValueCode: line = "{} = {}".format(newName, socket.getValueCode())
            else: line = getCopyLine(socket, newName, variables)
            variables[socket] = newName
            yield line

def iterRealNodeExecutionLines(node, variables):
    taggedLines = node.getTaggedExecutionCodeLines()
    for line in taggedLines:
        yield replaceTaggedLine(line, node, variables)

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

def handleExecutionCodeCreationException(node):
    print("\n"*5)
    traceback.print_exc()
    NodeFailesToCreateExecutionCode(node.identifier).report()
    raise Exception("Node failed to create execution code")



# Modify Socket Variables
##########################################

def linkOutputSocketsToTargets(node, variables):
    lines = []
    resolveInnerLinks(node, variables)
    for socket in node.linkedOutputs:
        lines.extend(tuple(linkSocketToTargets(socket, variables)))
    return lines

def resolveInnerLinks(node, variables):
    inputs, outputs = node.inputsByIdentifier, node.outputsByIdentifier
    for inputName, outputName in node.innerLinks:
        variables[outputs[outputName]] = variables[inputs[inputName]]

def linkSocketToTargets(socket, variables):
    targets = socket.dataTargets
    needACopy = getTargetsThatNeedACopy(socket, targets)

    for target in targets:
        if target in needACopy:
            yield getCopyLine(socket, variables[target], variables)
        else:
            variables[target] = variables[socket]

def getTargetsThatNeedACopy(socket, targets):
    if not socket.isCopyable: return []
    modifiedTargets = [target for target in targets if target.dataIsModified]
    if socket.loop.copyAlways: return modifiedTargets
    if len(targets) == 1: return []
    if len(targets) > len(modifiedTargets): return modifiedTargets
    else: return modifiedTargets[1:]

def getCopyLine(fromSocket, targetName, variables):
    return "{} = {}".format(targetName, getCopyExpression(fromSocket, variables))

def getCopyExpression(socket, variables):
    return socket.getCopyExpression().replace("value", variables[socket])
