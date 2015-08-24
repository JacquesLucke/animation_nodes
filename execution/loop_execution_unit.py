from .. import problems
from . compile_scripts import compileScript
from . node_sorting import sortNodes
from . subprogram_execution_unit import SubprogramExecutionUnit
from .. exceptions import ExecutionUnitNotSetup, NodeRecursionDetected
from . code_generator import (getInitialSocketVariables,
                              getSetupCode,
                              getNodeExecutionLines,
                              linkOutputSocketsToTargets,
                              getInputCopySocketValuesLines)

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
        prepareLoop = indent(self.get_IterationsAmount_PrepareLoop(inputNode, socketVariables))
        loopBody = indent(self.get_IterationsAmount_LoopBody(nodes, socketVariables), amount = 2)
        return joinLines([header] + prepareLoop + loopBody)

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
        lines.extend(indent(linkOutputSocketsToTargets(inputNode, socketVariables)))
        return lines

    def get_IterationsAmount_LoopBody(self, nodes, socketVariables):
        lines = []
        for node in nodes:
            if node.bl_idname in ("an_LoopInput", ): continue
            lines.extend(getNodeExecutionLines(node, socketVariables))
            lines.extend(linkOutputSocketsToTargets(node, socketVariables))
        lines.append("pass")
        return lines

    def compileScript(self):
        self.setupCodeObject = compileScript(self.setupScript, name = "group: {}".format(repr(self.network.name)))


    def raiseNotSetupException(self):
        raise ExecutionUnitNotSetup()

def joinLines(lines):
    return "\n".join(lines)

def indent(lines, amount = 1):
    return [" " * (4 * amount) + line for line in lines]
