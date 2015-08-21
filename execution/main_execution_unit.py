from . node_sorting import sortNodes
from . code_generator import PreparationScriptGenerator, getNodeExecutionLines

class MainExecutionUnit:
    def __init__(self, network):
        self.network = network
        self.prepareScript = ""
        self.executeScript = ""
        self.prepareCodeObject = None
        self.executeCodeObject = None

        self.generateScripts()
        self.compileScripts()
        self.execute = self.raiseNotPreparedException


    def prepare(self):
        self.executionData = {}
        exec(self.prepareCodeObject, self.executionData, self.executionData)
        self.execute = self.executeUnit

    def finish(self):
        self.executionData.clear()
        self.execute = self.raiseNotPreparedException

    def executeUnit(self):
        exec(self.executeCodeObject, self.executionData, self.executionData)

    def raiseNotPreparedException(self):
        raise Exception()



    def generateScripts(self):
        nodes = self.network.getAnimationNodes()
        nodes = sortNodes(nodes)
        preparation = PreparationScriptGenerator(nodes)
        self.prepareScript = preparation.generate()
        self.executeScript = self.getExecutionScript(nodes, preparation.socketVariables)

    def getExecutionScript(self, nodes, socketVariables):
        lines = []
        for node in nodes:
            lines.extend(getNodeExecutionLines(node, socketVariables))
        return "\n".join(lines)

    def compileScripts(self):
        self.prepareCodeObject = compileCode(self.prepareScript)
        self.executeCodeObject = compileCode(self.executeScript)



def compileCode(script):
    return compile(script, "<string>", "exec")
