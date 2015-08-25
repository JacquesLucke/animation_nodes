from .. import problems
from . compile_scripts import compileScript
from . node_sorting import sortNodes
from . subprogram_execution_unit import SubprogramExecutionUnit
from .. exceptions import ExecutionUnitNotSetup, NodeRecursionDetected
from . code_generator import (getInitialSocketVariables,
                              getSetupCode,
                              getNodeExecutionLines,
                              linkOutputSocketsToTargets)

class LoopExecutionUnit(SubprogramExecutionUnit):
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
        nodes = self.network.getAnimationNodes()

        try:
            nodes = sortNodes(nodes)
        except NodeRecursionDetected:
            problems.report(message = "Link Recursion in {}".format(repr(self.network.name)), forbidExecution = True)
            return

        socketVariables = getInitialSocketVariables(nodes)
        self.setupScript = getSetupCode(nodes, socketVariables)
        self.setupScript += "\n"*3
        self.setupScript += self.getFunctionGenerationScript(nodes, socketVariables)

    def getFunctionGenerationScript(self, nodes, socketVariables):
        inputNode = self.network.loopInputNode

        if inputNode.iterateThroughLists:
            return self.get_IteratorLength(inputNode, nodes, socketVariables)
        else:
            return self.get_IterationsAmount(inputNode, nodes, socketVariables)


    def get_IterationsAmount(self, inputNode, nodes, socketVariables):
        header = self.get_IterationsAmount_Header(inputNode, socketVariables)
        generators = indent(self.get_InitializeGenerators(inputNode, socketVariables))
        prepareLoop = indent(self.get_IterationsAmount_PrepareLoop(inputNode, socketVariables))
        loopBody = indent(self.get_LoopBody(inputNode, nodes, socketVariables), amount = 2)
        returnStatement = indent([self.get_ReturnStatement(inputNode, socketVariables)])
        return joinLines([header] + generators + prepareLoop + loopBody + returnStatement)

    def get_IterationsAmount_Header(self, inputNode, socketVariables):
        socketVariables[inputNode.iterationsSocket] = "loop_iterations"
        parameterNames = ["loop_iterations"]
        for i, socket in enumerate(inputNode.getParameterSockets()):
            name = "loop_parameter_" + str(i)
            socketVariables[socket] = name
            parameterNames.append(name)

        header = "def main({}):".format(", ".join(parameterNames))
        return header

    def get_IterationsAmount_PrepareLoop(self, inputNode, socketVariables):
        lines = []
        socketVariables[inputNode.indexSocket] = "current_loop_index"
        lines.append("for current_loop_index in range(loop_iterations):")
        return lines


    def get_IteratorLength(self, inputNode, nodes, socketVariables):
        header = self.get_IteratorLength_Header(inputNode, socketVariables)
        generators = indent(self.get_InitializeGenerators(inputNode, socketVariables))
        prepareLoop = indent(self.get_IteratorLength_PrepareLoop(inputNode, socketVariables))
        loopBody = indent(self.get_LoopBody(inputNode, nodes, socketVariables), amount = 2)
        returnStatement = indent([self.get_ReturnStatement(inputNode, socketVariables)])
        return joinLines([header] + generators + prepareLoop + loopBody + returnStatement)

    def get_IteratorLength_Header(self, inputNode, socketVariables):
        parameterNames = []
        for i, socket in enumerate(inputNode.getIteratorSockets()):
            name = "loop_iterator_" + str(i)
            parameterNames.append(name)
        for i, socket in enumerate(inputNode.getParameterSockets()):
            name = "loop_parameter_" + str(i)
            socketVariables[socket] = name
            parameterNames.append(name)

        header = "def main({}):".format(", ".join(parameterNames))
        return header

    def get_IteratorLength_PrepareLoop(self, inputNode, socketVariables):
        lines = []

        iterators = inputNode.getIteratorSockets()
        iteratorNames = ["loop_iterator_" + str(i) for i in range(len(iterators))]
        zipLine = "loop_zipped_list = list(zip({}))".format(", ".join(iteratorNames))
        iterationsLine = "loop_iterations = len(loop_zipped_list)"

        names = []
        for i, socket in enumerate(iterators):
            name = "loop_iterator_element_" + str(i)
            socketVariables[socket] = name
            names.append(name)
        loopLine = "for current_loop_index, ({}, ) in enumerate(loop_zipped_list):".format(", ".join(names))

        socketVariables[inputNode.indexSocket] = "current_loop_index"
        socketVariables[inputNode.iterationsSocket] = "loop_iterations"

        lines.append(zipLine)
        lines.append(iterationsLine)
        lines.append(loopLine)
        return lines


    def get_InitializeGenerators(self, inputNode, socketVariables):
        lines = []
        for i, node in enumerate(inputNode.getGeneratorNodes()):
            name = "loop_generator_output_" + str(i)
            socketVariables[node] = name
            lines.append("{} = []".format(name))
        return lines


    def get_LoopBody(self, inputNode, nodes, socketVariables):
        lines = []
        lines.extend(linkOutputSocketsToTargets(inputNode, socketVariables))
        for node in nodes:
            if node.bl_idname in ("an_LoopInput", "an_LoopGeneratorOutput"): continue
            lines.extend(getNodeExecutionLines(node, socketVariables))
            lines.extend(linkOutputSocketsToTargets(node, socketVariables))
        lines.extend(self.get_AddToGenerators(inputNode, socketVariables))
        lines.append("pass")
        return lines

    def get_AddToGenerators(self, inputNode, socketVariables):
        lines = []
        for node in inputNode.getGeneratorNodes():
            operation = "append" if node.addType == "APPEND" else "extend"
            lines.append("if {}:".format(socketVariables[node.activateSocket]))
            lines.append("    {}.{}({})".format(socketVariables[node], operation, socketVariables[node.addSocket]))
        return lines



    def get_ReturnStatement(self, inputNode, socketVariables):
        names = [socketVariables[node] for node in inputNode.getGeneratorNodes()]
        return "return {}".format(", ".join(names))



    def compileScript(self):
        self.setupCodeObject = compileScript(self.setupScript, name = "group: {}".format(repr(self.network.name)))


    def raiseNotSetupException(self):
        raise ExecutionUnitNotSetup()

def joinLines(lines):
    return "\n".join(lines)

def indent(lines, amount = 1):
    return [" " * (4 * amount) + line for line in lines]
