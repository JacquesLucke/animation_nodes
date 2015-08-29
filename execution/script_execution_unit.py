from . compile_scripts import compileScript
from .. problems import ExecutionUnitNotSetup

class ScriptExecutionUnit:
    def __init__(self, network):
        self.network = network
        self.setupScript = ""
        self.setupCodeObject = None
        self.executionData = {}

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
        return [self.setupScript]


    def generateScript(self):
        node = self.network.scriptNode

        header = self.getFunctionHeader(node)
        executionScript = "\n".join(indent(node.executionCode.split("\n")))
        returnStatement = " "*4 + self.getReturnStatement(node)

        self.setupScript = "\n".join([header, executionScript, returnStatement])

    def getFunctionHeader(self, node):
        inputNames = [socket.text for socket in node.inputs[:-1]]
        parameterList = ", ".join(inputNames)
        header = "def main({}):".format(parameterList)
        return header

    def getReturnStatement(self, node):
        outputNames = [socket.text for socket in node.outputs[:-1]]
        returnList = ", ".join(outputNames)
        return "return " + returnList

    def compileScript(self):
        self.setupCodeObject = compileScript(self.setupScript, name = "script: {}".format(repr(self.network.name)))

    def raiseNotSetupException(self):
        raise ExecutionUnitNotSetup()

def indent(lines):
    return [" "*4 + line for line in lines]
