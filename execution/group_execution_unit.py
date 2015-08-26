from .. import problems
from . compile_scripts import compileScript
from . node_sorting import sortNodes
from . subprogram_execution_unit import SubprogramExecutionUnit
from .. problems import ExecutionUnitNotSetup, NodeRecursionDetected
from . code_generator import (getInitialVariables,
                              getSetupCode,
                              getNodeExecutionLines,
                              linkOutputSocketsToTargets)

class GroupExecutionUnit(SubprogramExecutionUnit):
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

        variables = getInitialVariables(nodes)
        self.setupScript = getSetupCode(nodes, variables)
        self.setupScript += "\n"*3
        self.setupScript += self.getFunctionGenerationScript(nodes, variables)

    def getFunctionGenerationScript(self, nodes, variables):
        headerStatement = self.getFunctionHeader(self.network.groupInputNode, variables)
        executionScript = "\n".join(indent(self.getExecutionScriptLines(nodes, variables)))
        returnStatement = "\n" + " "*4 + self.getReturnStatement(self.network.groupOutputNode, variables)
        return "\n".join([headerStatement, executionScript, returnStatement])

    def getFunctionHeader(self, inputNode, variables):
        for i, socket in enumerate(inputNode.outputs):
            variables[socket] = "group_input_" + str(i)

        parameterList = ", ".join([variables[socket] for socket in inputNode.sockets[:-1]])
        header = "def main({}):".format(parameterList)
        return header

    def getExecutionScriptLines(self, nodes, variables):
        lines = []
        lines.extend(linkOutputSocketsToTargets(self.network.groupInputNode, variables))
        for node in nodes:
            if node.bl_idname in ("an_GroupInputNode", "an_GroupOutputNode"): continue
            lines.extend(getNodeExecutionLines(node, variables))
            lines.extend(linkOutputSocketsToTargets(node, variables))
        return lines

    def getReturnStatement(self, outputNode, variables):
        if outputNode is None: return "return"
        returnList = ", ".join([variables[socket] for socket in outputNode.inputs[:-1]])
        return "return " + returnList

    def compileScript(self):
        self.setupCodeObject = compileScript(self.setupScript, name = "group: {}".format(repr(self.network.name)))


    def raiseNotSetupException(self):
        raise ExecutionUnitNotSetup()


def indent(lines):
    return [" "*4 + line for line in lines]
