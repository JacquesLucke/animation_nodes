from .. utils.code import isCodeValid
from . compile_scripts import compileScript
from .. problems import ExecutionUnitNotSetup
from . code_generator import getSocketValueExpression, getSetupCode, getInitialVariables

class ScriptExecutionUnit:
    def __init__(self, network):
        self.network = network
        self.setupScript = ""
        self.setupCodeObject = None
        self.executionData = {}

        self.scriptUpdated()

    def scriptUpdated(self):
        self.generateScript()
        self.compileScript()

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
        return [self.code]


    def generateScript(self):
        node = self.network.scriptNode
        userCode = node.executionCode

        variables = getInitialVariables([node])
        setupCode = getSetupCode([node], variables)

        finalCode = []
        finalCode.append(setupCode)
        finalCode.append(self.getFunctionHeader(node))

        if isCodeValid(userCode):
            codeLines = []
            codeLines.extend(userCode.split("\n"))
            codeLines.append(self.getReturnStatement(node))

            if node.debugMode: finalCode.extend(indent(self.getDebugModeFunctionBody(codeLines, node)))
            else: finalCode.extend(indent(codeLines))
        else:
            finalCode.append("    {}.errorMessage = 'Syntax Error'".format(node.identifier))
            finalCode.append("    " + self.getDefaultReturnStatement(node))

        self.setupScript = "\n".join(finalCode)

    def getDebugModeFunctionBody(self, codeLines, node):
        lines = []
        lines.append("try:")
        lines.append("    {}.errorMessage = ''".format(node.identifier))
        lines.extend(indent(codeLines))
        lines.append("except:")
        lines.append("    {}.errorMessage = str(sys.exc_info()[1])".format(node.identifier))
        lines.append("    " + self.getDefaultReturnStatement(node))
        return lines

    def getFunctionHeader(self, node):
        inputNames = [socket.text for socket in node.inputs[:-1]]
        parameterList = ", ".join(inputNames)
        header = "def main({}):".format(parameterList)
        return header

    def getReturnStatement(self, node):
        outputNames = [socket.text for socket in node.outputs[:-1]]
        returnList = ", ".join(outputNames)
        return "return " + returnList

    def getDefaultReturnStatement(self, node):
        outputSockets = node.outputs[:-1]
        outputExpressions = [getSocketValueExpression(socket) for socket in outputSockets]
        return "return " + ", ".join(outputExpressions)

    def compileScript(self):
        self.setupCodeObject = compileScript(self.setupScript, name = "script: {}".format(repr(self.network.name)))

    def raiseNotSetupException(self):
        raise ExecutionUnitNotSetup()

def indent(lines, amount = 1):
    return [" " * (4 * amount) + line for line in lines]
