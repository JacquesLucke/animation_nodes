import os
import re
import traceback
from itertools import chain
from functools import lru_cache
from collections import defaultdict
from .. problems import NodeFailesToCreateExecutionCode
from .. tree_info import iterLinkedSocketsWithInfo, isSocketLinked
from .. preferences import (addonName,
                            monitorExecutionIsEnabled,
                            measureNodeExecutionTimesIsEnabled)


# Initial Socket Variables
##########################################

def getInitialVariables(nodes):
    variables = {}
    for node in nodes:
        nodeIdentifierPart = node.identifier[:4]
        for index, socket in enumerate(chain(node.inputs, node.outputs)):
            if socket.identifier.isidentifier():
                variables[socket] = "_" + socket.identifier + nodeIdentifierPart
            else:
                variables[socket] = "__socket_" + str(socket.is_output) + "_" + str(index) + nodeIdentifierPart
    return variables


# Setup Code
##########################################

def iterSetupCodeLines(nodes, variables):
    yield get_ImportModules(nodes)
    yield get_ImportTimeMeasurementFunction()
    yield get_ImportAnimationNodes()
    yield get_LoadRandomNumberCache()
    yield get_LoadMeasurementsDict()
    yield from iter_GetNodeReferences(nodes)
    yield from iter_GetSocketValues(nodes, variables)


def get_ImportModules(nodes):
    neededModules = {"bpy", "sys"}
    neededModules.update(getModulesNeededByNodes(nodes))
    modulesString = ", ".join(neededModules)
    return "import " + modulesString

def get_ImportTimeMeasurementFunction():
    return "from time import perf_counter as getCurrentTime"

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

def get_LoadMeasurementsDict():
    return "_node_execution_times = animation_nodes.execution.measurements.getMeasurementsDict()"

def iter_GetNodeReferences(nodes):
    yield "nodes = bpy.data.node_groups[{}].nodes".format(repr(nodes[0].nodeTree.name))
    for node in nodes:
        yield "{} = nodes[{}]".format(node.identifier, repr(node.name))

def iter_GetSocketValues(nodes, variables):
    for node in nodes:
        for i, socket in enumerate(node.inputs):
            if not isSocketLinked(socket, node):
                yield getLoadSocketValueLine(socket, node, variables, i)

def getLoadSocketValueLine(socket, node, variables, index = None):
    return "{} = {}".format(variables[socket], getSocketValueExpression(socket, node, index))

def getSocketValueExpression(socket, node, index = None):
    if socket.hasValueCode: return socket.getValueCode()
    else:
        socketsName = "inputs" if socket.isInput else "outputs"
        if index is None: index = socket.getIndex(node)
        return "{}.{}[{}].getValue()".format(node.identifier, socketsName, index)



# Node Execution Code
##########################################

def getGlobalizeStatement(nodes, variables):
    socketNames = [variables[socket] for socket in iterUnlinkedSockets(nodes)]
    if len(socketNames) == 0: return ""
    return "global " + ", ".join(socketNames)

def iterUnlinkedSockets(nodes):
    for node in nodes:
        yield from node.unlinkedInputs

def getFunction_IterNodeExecutionLines():
    if measureNodeExecutionTimesIsEnabled():
        return iterNodeExecutionLines_MeasureTimes
    else:
        if monitorExecutionIsEnabled():
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

def iterNodeExecutionLines_MeasureTimes(node, variables):
    yield from iterNodePreExecutionLines(node, variables)
    try:
        yield "_execution_start_time = getCurrentTime()"
        yield from iterRealNodeExecutionLines(node, variables)
        yield "_node_execution_times[{}].totalTime += getCurrentTime() - _execution_start_time".format(repr(node.identifier))
        yield "_node_execution_times[{}].calls += 1".format(repr(node.identifier))
    except:
        handleExecutionCodeCreationException(node)

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
        if socket.dataIsModified and socket.isCopyable() and not isSocketLinked(socket, node):
            newName = variables[socket] + "_copy"
            if socket.hasValueCode: line = "{} = {}".format(newName, socket.getValueCode())
            else: line = getCopyLine(socket, newName, variables)
            variables[socket] = newName
            yield line

def iterRealNodeExecutionLines(node, variables):
    localCode = node.getLocalExecutionCode()
    globalCode = makeGlobalExecutionCode(localCode, node, variables)
    yield from globalCode.splitlines()

def makeGlobalExecutionCode(localCode, node, variables):
    code = replaceVariableName(localCode, "self", node.identifier)
    nodeInputs = node.inputsByIdentifier
    for name, variable in node.inputVariables.items():
        code = replaceVariableName(code, variable, variables[nodeInputs[name]])
    nodeOutputs = node.outputsByIdentifier
    for name, variable in node.outputVariables.items():
        code = replaceVariableName(code, variable, variables[nodeOutputs[name]])
    return code

@lru_cache(maxsize = 2**15)
def replaceVariableName(code, oldName, newName):
    pattern = r"([^\.\"\%']|^)\b{}\b".format(oldName)
    return re.sub(pattern, r"\1{}".format(newName), code)


def handleExecutionCodeCreationException(node):
    print("\n"*5)
    traceback.print_exc()
    NodeFailesToCreateExecutionCode(node.identifier).report()
    raise Exception("Node failed to create execution code")



# Modify Socket Variables
##########################################

def linkOutputSocketsToTargets(node, variables, nodeByID):
    resolveInnerLinks(node, variables)
    for socket in node.linkedOutputs:
        yield from linkSocketToTargets(socket, node, variables, nodeByID)

def resolveInnerLinks(node, variables):
    inputs, outputs = node.inputsByIdentifier, node.outputsByIdentifier
    for inputName, outputName in node.iterInnerLinks():
        variables[outputs[outputName]] = variables[inputs[inputName]]

def linkSocketToTargets(socket, node, variables, nodeByID):
    targets = tuple(iterLinkedSocketsWithInfo(socket, node, nodeByID))
    needACopy = getTargetsThatNeedACopy(socket, targets)

    for target in targets:
        if target in needACopy:
            yield getCopyLine(socket, variables[target], variables)
        else:
            variables[target] = variables[socket]

def getTargetsThatNeedACopy(socket, targets):
    if not socket.isCopyable(): return []
    modifiedTargets = [target for target in targets if target.dataIsModified]
    if socket.loop.copyAlways: return modifiedTargets
    if len(targets) == 1: return []
    if len(targets) > len(modifiedTargets): return modifiedTargets
    else: return modifiedTargets[1:]

def getCopyLine(fromSocket, targetName, variables):
    return "{} = {}".format(targetName, getCopyExpression(fromSocket, variables))

def getCopyExpression(socket, variables):
    return socket.getCopyExpression().replace("value", variables[socket])
