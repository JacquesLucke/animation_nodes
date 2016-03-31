import sys, traceback
from .. import problems
from . compile_scripts import compileScript
from .. problems import ExecutionUnitNotSetup, ExceptionDuringExecution
from . code_generator import (getInitialVariables,
                              iterSetupCodeLines,
                              linkOutputSocketsToTargets,
                              getFunction_IterNodeExecutionLines)

class MainExecutionUnit:
    def __init__(self, network):
        self.network = network
        self.setupScript = ""
        self.executeScript = ""
        self.setupCodeObject = None
        self.executeCodeObject = None
        self.executionData = {}

        self.generateScripts()
        self.compileScripts()
        self.execute = self.raiseNotSetupException


    def setup(self):
        self.executionData = {}
        exec(self.setupCodeObject, self.executionData, self.executionData)
        self.execute = self.executeUnit

    def insertSubprogramFunctions(self, data):
        self.executionData.update(data)

    def finish(self):
        self.executionData.clear()
        self.execute = self.raiseNotSetupException

    def executeUnit(self):
        try:
            exec(self.executeCodeObject, self.executionData, self.executionData)
        except:
            print("\n"*5)
            traceback.print_exc()
            ExceptionDuringExecution().report()


    def getCodes(self):
        return [self.setupScript, self.executeScript]



    def generateScripts(self):
        try: nodes = self.network.getSortedAnimationNodes()
        except: return

        variables = getInitialVariables(nodes)
        self.setupScript = "\n".join(iterSetupCodeLines(nodes, variables))
        self.executeScript = "\n".join(self.iterExecutionScriptLines(nodes, variables))

    def iterExecutionScriptLines(self, nodes, variables):
        iterNodeExecutionLines = getFunction_IterNodeExecutionLines()
        
        for node in nodes:
            yield from iterNodeExecutionLines(node, variables)
            yield from linkOutputSocketsToTargets(node, variables)

    def compileScripts(self):
        self.setupCodeObject = compileScript(self.setupScript, name = "setup: {}".format(repr(self.network.treeName)))
        self.executeCodeObject = compileScript(self.executeScript, name = "execution: {}".format(repr(self.network.treeName)))


    def raiseNotSetupException(self, *args, **kwargs):
        raise ExecutionUnitNotSetup()
