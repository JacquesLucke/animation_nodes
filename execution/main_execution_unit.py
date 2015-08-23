import sys, traceback
from .. import problems
from . node_sorting import sortNodes
from . compile_scripts import compileScript
from .. exceptions import ExecutionUnitNotSetup, NodeRecursionDetected
from . code_generator import (getInitialSocketVariables,
                              getSetupCode,
                              getNodeExecutionLines,
                              linkOutputSocketsToTargets,
                              getInputCopySocketValuesLines)

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
            problems.report(message = "Error during execution (see console)", forbidExecution = True)


    def getCodes(self):
        return [self.setupScript, self.executeScript]



    def generateScripts(self):
        nodes = self.network.getAnimationNodes()

        try:
            nodes = sortNodes(nodes)
        except NodeRecursionDetected:
            problems.report(message = "Link Recursion in {}".format(repr(self.network.treeName)), forbidExecution = True)
            return

        socketVariables = getInitialSocketVariables(nodes)
        self.setupScript = getSetupCode(nodes, socketVariables)
        self.executeScript = self.getExecutionScript(nodes, socketVariables)

    def getExecutionScript(self, nodes, socketVariables):
        lines = []
        lines.extend(getInputCopySocketValuesLines(nodes, socketVariables))
        for node in nodes:
            lines.extend(getNodeExecutionLines(node, socketVariables))
            lines.extend(linkOutputSocketsToTargets(node, socketVariables))
        return "\n".join(lines)

    def compileScripts(self):
        self.setupCodeObject = compileScript(self.setupScript, name = "setup: {}".format(repr(self.network.treeName)))
        self.executeCodeObject = compileScript(self.executeScript, name = "execution: {}".format(repr(self.network.treeName)))


    def raiseNotSetupException(self, *args, **kwargs):
        raise ExecutionUnitNotSetup()
