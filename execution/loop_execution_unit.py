from . compile_scripts import compileScript
from .. problems import ExecutionUnitNotSetup
from . code_generator import (getInitialVariables,
                              iterSetupCodeLines,
                              getCopyExpression,
                              getGlobalizeStatement,
                              getNodeExecutionLines,
                              linkOutputSocketsToTargets,
                              getLoadSocketValueLine)

class LoopExecutionUnit:
    def __init__(self, network):
        self.network = network
        self.setupScript = ""
        self.setupCodeObject = None
        self.executionData = {}

        self.generateScript()
        self.compileScript()
        self.execute = self.raiseNotSetupException


    def setup(self):
        self.executionData = {}
        exec(self.setupCodeObject, self.executionData, self.executionData)
        self.execute = self.executionData["main"]

    def insertSubprogramFunctions(self, data):
        self.executionData.update(data)

    def finish(self):
        self.executionData.clear()
        self.execute = self.raiseNotSetupException


    def getCodes(self):
        return [self.setupScript]



    def generateScript(self):
        try: nodes = self.network.getSortedAnimationNodes()
        except: return

        variables = getInitialVariables(nodes)
        self.setupScript = "\n".join(iterSetupCodeLines(nodes, variables))
        self.setupScript += "\n"*3
        self.setupScript += self.getFunctionGenerationScript(nodes, variables)

    def getFunctionGenerationScript(self, nodes, variables):
        inputNode = self.network.loopInputNode

        if inputNode.iterateThroughLists:
            return "\n".join(self.iter_IteratorLength(inputNode, nodes, variables))
        else:
            return self.get_IterationsAmount(inputNode, nodes, variables)


    def get_IterationsAmount(self, inputNode, nodes, variables):
        header = self.get_IterationsAmount_Header(inputNode, variables)
        globalizeStatement = " "*4 + getGlobalizeStatement(nodes, variables)
        generators = indent(tuple(self.iter_InitializeGeneratorsLines(inputNode, variables)))
        parameters = indent(tuple(self.iter_InitializeParametersLines(inputNode, variables)))
        prepareLoop = indent(self.get_IterationsAmount_PrepareLoop(inputNode, variables))
        loopBody = indent(tuple(self.iter_LoopBody(inputNode, nodes, variables)), amount = 2)
        returnStatement = indent([self.get_ReturnStatement(inputNode, variables)])
        return joinLines([header] + [globalizeStatement] + generators + parameters + prepareLoop + loopBody + returnStatement)

    def get_IterationsAmount_Header(self, inputNode, variables):
        variables[inputNode.iterationsSocket] = "loop_iterations"
        parameterNames = ["loop_iterations"]
        for i, socket in enumerate(inputNode.getParameterSockets()):
            if socket.loop.useAsInput:
                name = "loop_parameter_" + str(i)
                variables[socket] = name
                parameterNames.append(name)

        header = "def main({}):".format(", ".join(parameterNames))
        return header

    def get_IterationsAmount_PrepareLoop(self, inputNode, variables):
        lines = []
        variables[inputNode.indexSocket] = "current_loop_index"
        lines.append("for current_loop_index in range(loop_iterations):")
        return lines


    def iter_IteratorLength(self, inputNode, nodes, variables):
        yield self.get_IteratorLength_Header(inputNode, variables)
        yield "    " + getGlobalizeStatement(nodes, variables)
        yield from iterIndented(self.iter_InitializeGeneratorsLines(inputNode, variables))
        yield from iterIndented(self.iter_InitializeParametersLines(inputNode, variables))
        yield from iterIndented(self.iter_IteratorLength_PrepareLoopLines(inputNode, variables))
        yield from iterIndented(self.iter_LoopBody(inputNode, nodes, variables), amount = 2)
        yield "    " + self.get_ReturnStatement(inputNode, variables)

    def get_IteratorLength_Header(self, inputNode, variables):
        parameterNames = []
        for i, socket in enumerate(inputNode.getIteratorSockets()):
            name = "loop_iterator_" + str(i)
            parameterNames.append(name)
        for i, socket in enumerate(inputNode.getParameterSockets()):
            if socket.loop.useAsInput:
                name = "loop_parameter_" + str(i)
                variables[socket] = name
                parameterNames.append(name)

        header = "def main({}):".format(", ".join(parameterNames))
        return header

    def iter_IteratorLength_PrepareLoopLines(self, inputNode, variables):
        iterators = inputNode.getIteratorSockets()
        iteratorNames = ["loop_iterator_" + str(i) for i in range(len(iterators))]
        zipLine = "loop_zipped_list = list(zip({}))".format(", ".join(iteratorNames))
        iterationsLine = "loop_iterations = len(loop_zipped_list)"

        names = []
        for i, socket in enumerate(iterators):
            name = "loop_iterator_element_" + str(i)
            variables[socket] = name
            names.append(name)
        loopLine = "for current_loop_index, ({}, ) in enumerate(loop_zipped_list):".format(", ".join(names))

        variables[inputNode.indexSocket] = "current_loop_index"
        variables[inputNode.iterationsSocket] = "loop_iterations"

        yield zipLine
        yield iterationsLine
        yield loopLine


    def iter_InitializeGeneratorsLines(self, inputNode, variables):
        for i, node in enumerate(inputNode.getSortedGeneratorNodes()):
            name = "loop_generator_output_" + str(i)
            variables[node] = name
            yield "{} = []".format(name)

    def iter_InitializeParametersLines(self, inputNode, variables):
        for socket in inputNode.getParameterSockets():
            if not socket.loop.useAsInput:
                yield getLoadSocketValueLine(socket, variables)


    def iter_LoopBody(self, inputNode, nodes, variables):
        yield from linkOutputSocketsToTargets(inputNode, variables)

        ignoreNodes = {"an_LoopInputNode", "an_LoopGeneratorOutputNode", "an_ReassignLoopParameterNode"}
        for node in nodes:
            if node.bl_idname in ignoreNodes: continue
            yield from getNodeExecutionLines(node, variables)
            yield from linkOutputSocketsToTargets(node, variables)

        yield from self.iter_LoopBreak(inputNode, variables)
        yield from self.iter_AddToGenerators(inputNode, variables)
        yield from self.iter_ReassignParameters(inputNode, variables)
        yield "pass"

    def iter_LoopBreak(self, inputNode, variables):
        for node in inputNode.getBreakNodes():
            yield "if not {}: break".format(variables[node.inputs[0]])

    def iter_AddToGenerators(self, inputNode, variables):#
        for node in inputNode.getSortedGeneratorNodes():
            operation = "append" if node.addType == "APPEND" else "extend"
            yield "if {}:".format(variables[node.conditionSocket])

            socket = node.addSocket
            if socket.isUnlinked and socket.isCopyable: expression = getCopyExpression(socket, variables)
            else: expression = variables[socket]
            yield "    {}.{}({})".format(variables[node], operation, expression)#

    def iter_ReassignParameters(self, inputNode, variables):
        for node in inputNode.getReassignParameterNodes():
            socket = node.inputs[0]
            if socket.isUnlinked and socket.isCopyable: expression = getCopyExpression(socket, variables)
            else: expression = variables[socket]

            if node.conditionSocket is None: conditionPrefix = ""
            else: conditionPrefix = "if {}: ".format(variables[node.conditionSocket])

            yield "{}{} = {}".format(conditionPrefix, variables[node.linkedParameterSocket], expression)



    def get_ReturnStatement(self, inputNode, variables):
        names = []
        names.extend(["loop_iterator_" + str(i) for i, socket in enumerate(inputNode.getIteratorSockets()) if socket.loop.useAsOutput])
        names.extend([variables[node] for node in inputNode.getSortedGeneratorNodes()])
        names.extend([variables[socket] for socket in inputNode.getParameterSockets() if socket.loop.useAsOutput])
        return "return {}".format(", ".join(names))



    def compileScript(self):
        self.setupCodeObject = compileScript(self.setupScript, name = "group: {}".format(repr(self.network.name)))


    def raiseNotSetupException(self):
        raise ExecutionUnitNotSetup()

def joinLines(lines):
    return "\n".join(lines)

def indent(lines, amount = 1):
    return [" " * (4 * amount) + line for line in lines]

def iterIndented(lines, amount = 1):
    indentation = "    " * amount
    for line in lines:
        yield indentation + line
