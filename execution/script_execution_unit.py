from .. utils.code import isCodeValid
from . compile_scripts import compileScript
from .. problems import ExecutionUnitNotSetup, ScriptHasNoMainFunction
from . code_generator import getSocketValueExpression, getSetupCode, getInitialVariables

class ScriptExecutionUnit:
    def __init__(self, network):
        self.network = network
        self.code = ""
        self.codeObject = None
        self.executionData = {}

        self.code = self.network.scriptNode.executionCode
        self.compileScript()

    def setup(self):
        self.executionData = {}
        exec(self.codeObject, self.executionData, self.executionData)
        if "main" in self.executionData: self.execute = self.executionData["main"]
        else:
            ScriptHasNoMainFunction(self.network).report()
            self.execute = self.raiseNotSetupException

    def insertSubprogramFunctions(self, data):
        self.executionData.update(data)

    def finish(self):
        self.executionData.clear()
        self.execute = self.raiseNotSetupException

    def getCodes(self):
        return [self.setupScript]

    def compileScript(self):
        self.codeObject = compileScript(self.code, name = "script: {}".format(repr(self.network.name)))

    def raiseNotSetupException(self):
        raise ExecutionUnitNotSetup()
