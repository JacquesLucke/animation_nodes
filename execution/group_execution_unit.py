from . node_sorting import sortNodes
from . subprogram_execution_unit import SubprogramExecutionUnit
from .. exceptions import ExecutionUnitNotSetup
from . code_generator import (getInitialSocketVariables,
                              getSetupCode,
                              getNodeExecutionLines,
                              linkOutputSocketsToTargets)

class GroupExecutionUnit(SubprogramExecutionUnit):
    def __init__(self, network):
        self.network = network
        self.setupScript = ""
        self.setupCodeObject = None

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


    def getCode(self):
        return self.setupScript



    def generateScript(self):
        nodes = self.network.getAnimationNodes()
        nodes = sortNodes(nodes)

        socketVariables = getInitialSocketVariables(nodes)
        self.setupScript = getSetupCode(nodes, socketVariables)
        self.setupScript += "\n"*3
        self.setupScript += self.getFunctionGenerationScript(nodes, socketVariables)

    def getFunctionGenerationScript(self, nodes, socketVariables):
        headerStatement = self.getFunctionHeader(self.network.groupInputNode, socketVariables)
        executionScript = "\n".join(indent(self.getExecutionScriptLines(nodes, socketVariables)))
        returnStatement = " "*4 + self.getReturnStatement(self.network.groupOutputNode, socketVariables)
        return "\n".join([headerStatement, executionScript, returnStatement])

    def getFunctionHeader(self, inputNode, socketVariables):
        for i, socket in enumerate(inputNode.outputs):
            socketVariables[socket] = "group_input_" + str(i)

        parameterList = ", ".join([socketVariables[socket] for socket in inputNode.sockets[:-1]])
        header = "def main({}):".format(parameterList)
        linkOutputSocketsToTargets(inputNode, socketVariables)
        return header

    def getExecutionScriptLines(self, nodes, socketVariables):
        lines = []
        for node in nodes:
            if node.bl_idname in ("an_GroupInput", "an_GroupOutput"): continue
            lines.extend(getNodeExecutionLines(node, socketVariables))
            linkOutputSocketsToTargets(node, socketVariables)
        return lines

    def getReturnStatement(self, outputNode, socketVariables):
        if outputNode is None: return "return"
        returnList = ", ".join([socketVariables[socket] for socket in outputNode.inputs[:-1]])
        return "return " + returnList

    def compileScript(self):
        self.setupCodeObject = compile(self.setupScript, "<string>", "exec")



    def raiseNotSetupException(self):
        raise ExecutionUnitNotSetup()


def indent(lines):
    return [" "*4 + line for line in lines]
