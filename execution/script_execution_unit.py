from .. utils.code import isCodeValid
from . compile_scripts import compileScript
from .. problems import ExecutionUnitNotSetup
from . code_generator import getSocketValueExpression, iterSetupCodeLines, getInitialVariables

class ScriptExecutionUnit:
    def __init__(self, network, nodeByID):
        self.network = network
        self.setupScript = ""
        self.setupCodeObject = None
        self.executionData = {}

        self.scriptUpdated(nodeByID)

    def scriptUpdated(self, nodeByID = None):
        self.generateScript(nodeByID)
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
        return [self.setupScript]


    def generateScript(self, nodeByID):
        node = self.network.getScriptNode(nodeByID)
        userCode = node.executionCode

        variables = getInitialVariables([node])
        setupCode = "\n".join(iterSetupCodeLines([node], variables))

        finalCode = []
        finalCode.append(setupCode)
        finalCode.append(self.getFunctionHeader(node))

        if isCodeValid(userCode):
            codeLines = []
            codeLines.extend(userCode.split("\n"))
            if node.initializeMissingOutputs:
                codeLines.extend(self.iterInitializeMissingOutputsLines(node))
            if node.correctOutputTypes:
                codeLines.extend(self.iterTypeCorrectionLines(node))
            codeLines.append(self.getReturnStatement(node))

            if node.debugMode: finalCode.extend(indent(self.iterDebugModeFunctionBody(codeLines, node)))
            else: finalCode.extend(indent(codeLines))
        else:
            finalCode.append("    {}.errorMessage = 'Syntax Error'".format(node.identifier))
            finalCode.append("    " + self.getDefaultReturnStatement(node))

        self.setupScript = "\n".join(finalCode)

    def iterDebugModeFunctionBody(self, codeLines, node):
        yield "try:"
        yield "    {}.errorMessage = ''".format(node.identifier)
        yield from indent(codeLines)
        yield "except:"
        yield "    {}.errorMessage = str(sys.exc_info()[1])".format(node.identifier)
        yield "    " + self.getDefaultReturnStatement(node)

    def getFunctionHeader(self, node):
        inputNames = [socket.text for socket in node.inputs[:-1]]
        parameterList = ", ".join(inputNames)
        header = "def main({}):".format(parameterList)
        return header

    def iterInitializeMissingOutputsLines(self, node):
        yield "localVariables = locals()"
        for i, socket in enumerate(node.outputs[:-1]):
            variableName = socket.text
            yield "if {} not in localVariables:".format(repr(variableName))
            yield "    {} = {}.outputs[{}].getDefaultValue()".format(
                       variableName, node.identifier, i)

    def iterTypeCorrectionLines(self, node):
        for i, socket in enumerate(node.outputs[:-1]):
            variableName = socket.text
            yield "__socket = {}.outputs[{}]".format(node.identifier, i)
            yield "{0}, __socket['correctionType'] = __socket.correctValue({0})".format(variableName)

    def getReturnStatement(self, node):
        outputNames = [socket.text for socket in node.outputs[:-1]]
        returnList = ", ".join(outputNames)
        return "return " + returnList

    def getDefaultReturnStatement(self, node):
        outputSockets = node.outputs[:-1]
        outputExpressions = [getSocketValueExpression(socket, node) for socket in outputSockets]
        return "return " + ", ".join(outputExpressions)

    def compileScript(self):
        self.setupCodeObject = compileScript(self.setupScript, name = "script: {}".format(repr(self.network.name)))

    def raiseNotSetupException(self):
        raise ExecutionUnitNotSetup()

def indent(lines, amount = 1):
    return (" " * (4 * amount) + line for line in lines) # returns a generator
