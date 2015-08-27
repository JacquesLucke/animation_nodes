from . node_sorting import sortNodes
from . compile_scripts import compileScript
from .. problems import ExecutionUnitNotSetup
from . subprogram_execution_unit import SubprogramExecutionUnit
from . code_generator import (getInitialVariables,
                              getSetupCode,
                              getNodeExecutionLines,
                              linkOutputSocketsToTargets,
                              getLoadSocketValueLine)

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

        try: nodes = sortNodes(nodes)
        except: return

        variables = getInitialVariables(nodes)
        self.setupScript = getSetupCode(nodes, variables)
        self.setupScript += "\n"*3
        self.setupScript += self.getFunctionGenerationScript(nodes, variables)

    def getFunctionGenerationScript(self, nodes, variables):
        inputNode = self.network.loopInputNode

        if inputNode.iterateThroughLists:
            return self.get_IteratorLength(inputNode, nodes, variables)
        else:
            return self.get_IterationsAmount(inputNode, nodes, variables)


    def get_IterationsAmount(self, inputNode, nodes, variables):
        header = self.get_IterationsAmount_Header(inputNode, variables)
        generators = indent(self.get_InitializeGenerators(inputNode, variables))
        parameters = indent(self.get_InitializeParameters(inputNode, variables))
        prepareLoop = indent(self.get_IterationsAmount_PrepareLoop(inputNode, variables))
        loopBody = indent(self.get_LoopBody(inputNode, nodes, variables), amount = 2)
        returnStatement = indent([self.get_ReturnStatement(inputNode, variables)])
        return joinLines([header] + generators + parameters + prepareLoop + loopBody + returnStatement)

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


    def get_IteratorLength(self, inputNode, nodes, variables):
        header = self.get_IteratorLength_Header(inputNode, variables)
        generators = indent(self.get_InitializeGenerators(inputNode, variables))
        parameters = indent(self.get_InitializeParameters(inputNode, variables))
        prepareLoop = indent(self.get_IteratorLength_PrepareLoop(inputNode, variables))
        loopBody = indent(self.get_LoopBody(inputNode, nodes, variables), amount = 2)
        returnStatement = indent([self.get_ReturnStatement(inputNode, variables)])
        return joinLines([header] + generators + parameters + prepareLoop + loopBody + returnStatement)

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

    def get_IteratorLength_PrepareLoop(self, inputNode, variables):
        lines = []

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

        lines.append(zipLine)
        lines.append(iterationsLine)
        lines.append(loopLine)
        return lines


    def get_InitializeGenerators(self, inputNode, variables):
        lines = []
        for i, node in enumerate(inputNode.getGeneratorNodes()):
            name = "loop_generator_output_" + str(i)
            variables[node] = name
            lines.append("{} = []".format(name))
        return lines

    def get_InitializeParameters(self, inputNode, variables):
        lines = []
        for socket in inputNode.getParameterSockets():
            if not socket.loop.useAsInput:
                lines.append(getLoadSocketValueLine(socket, variables))
        return lines


    def get_LoopBody(self, inputNode, nodes, variables):
        lines = []
        lines.extend(linkOutputSocketsToTargets(inputNode, variables))
        for node in nodes:
            if node.bl_idname in ("an_LoopInputNode", "an_LoopGeneratorOutputNode", "an_ReassignLoopParameterNode"): continue
            lines.extend(getNodeExecutionLines(node, variables))
            lines.extend(linkOutputSocketsToTargets(node, variables))
        lines.extend(self.get_AddToGenerators(inputNode, variables))
        lines.extend(self.get_ReassignParameters(inputNode, variables))
        lines.append("pass")
        return lines

    def get_AddToGenerators(self, inputNode, variables):
        lines = []
        for node in inputNode.getGeneratorNodes():
            operation = "append" if node.addType == "APPEND" else "extend"
            lines.append("if {}:".format(variables[node.enabledSocket]))
            lines.append("    {}.{}({})".format(variables[node], operation, variables[node.addSocket]))
        return lines

    def get_ReassignParameters(self, inputNode, variables):
        lines = []
        for node in inputNode.getReassignParameterNodes():
            lines.append("{} = {}".format(variables[node.linkedParameterSocket], variables[node.inputs[0]]))
        return lines



    def get_ReturnStatement(self, inputNode, variables):
        names = []
        names.extend(["loop_iterator_" + str(i) for i, socket in enumerate(inputNode.getIteratorSockets()) if socket.loop.useAsOutput])
        names.extend([variables[node] for node in inputNode.getGeneratorNodes()])
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
