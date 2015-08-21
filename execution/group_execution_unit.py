from . node_sorting import sortNodes
from . subprogram_execution_unit import SubprogramExecutionUnit
from . code_generator import PreparationScriptGenerator, getNodeExecutionLines, linkAllTargetSocketVariables

class GroupExecutionUnit(SubprogramExecutionUnit):
    def __init__(self, network):
        self.network = network

        self.prepareScript = ""
        self.prepareCodeObject = None

        self.generateScript()
        self.compileScript()
        self.execute = self.raiseNotPreparedException


    def prepare(self):
        self.executionData = {}
        exec(self.prepareCodeObject, self.executionData, self.executionData)
        self.execute = self.executionData["main"]

    def finish(self):
        self.executionData.clear()
        self.execute = self.raiseNotPreparedException

    def raiseNotPreparedException(self):
        raise Exception()



    def generateScript(self):
        nodes = self.network.getNodes()
        nodes = sortNodes(nodes)

        preparation = PreparationScriptGenerator(nodes)
        self.prepareScript = preparation.generate()
        socketVariables = preparation.socketVariables

        self.prepareScript += "\n"*3 + self.getFunctionGenerationScript(nodes, socketVariables)

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
        linkAllTargetSocketVariables(inputNode, socketVariables)
        return header

    def getExecutionScriptLines(self, nodes, socketVariables):
        lines = []
        for node in nodes:
            if node.bl_idname in ("an_GroupInput", "an_GroupOutput"): continue
            lines.extend(getNodeExecutionLines(node, socketVariables))
        return lines

    def getReturnStatement(self, outputNode, socketVariables):
        if outputNode is None: return "return"
        returnList = ", ".join([socketVariables[socket] for socket in outputNode.inputs[:-1]])
        return "return " + returnList

    def compileScript(self):
        self.prepareCodeObject = compile(self.prepareScript, "<string>", "exec")

def indent(lines):
    return [" "*4 + line for line in lines]
