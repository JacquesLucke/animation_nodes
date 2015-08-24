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
        headerStatement = self.getFunctionHeader(inputNode, socketVariables)
        executionScript = "\n".join(indent(self.getExecutionScriptLines(inputNode, nodes, socketVariables)))
        #returnStatement = "\n" + " "*4 + self.getReturnStatement(self.network.groupOutputNode, socketVariables)
        #return "\n".join([headerStatement, executionScript, returnStatement])
        return "\n".join([headerStatement, executionScript])

    def getFunctionHeader(self, inputNode, socketVariables):
        parameters = []
        data = inputNode.getSocketData()
        for i in range(len(data.inputs)):
            parameters.append("loop_input_" + str(i))

        header = "def main({}):".format(", ".join(parameters))
        return header

    def getExecutionScriptLines(self, inputNode, nodes, socketVariables):
        lines = []
        add = lines.append

        parameters = inputNode.getParameterSockets()
        iterators = inputNode.getIteratorSockets()

        if len(iterators) == 0:
            for i, socket in enumerate(parameters):
                socketVariables[socket] = "loop_input_" + str(i + 1)
            socketVariables[inputNode.indexSocket] = "current_loop_index"
            socketVariables[inputNode.iterationsSocket] = "loop_iterations"
            add("loop_iterations = loop_input_0")
            add("for current_loop_index in range(loop_input_0):")
            lines.extend(indent(linkOutputSocketsToTargets(inputNode, socketVariables)))

            loopLines = []
            for node in nodes:
                if node.bl_idname in ("an_LoopInput", ): continue
                loopLines.extend(getNodeExecutionLines(node, socketVariables))
                loopLines.extend(linkOutputSocketsToTargets(node, socketVariables))

            lines.extend(indent(loopLines))

        return lines

    def getReturnStatement(self, outputNode, socketVariables):
        if outputNode is None: return "return"
        returnList = ", ".join([socketVariables[socket] for socket in outputNode.inputs[:-1]])
        return "return " + returnList

    def compileScript(self):
        self.setupCodeObject = compileScript(self.setupScript, name = "group: {}".format(repr(self.network.name)))


    def raiseNotSetupException(self):
        raise ExecutionUnitNotSetup()


def indent(lines):
    return [" "*4 + line for line in lines]
