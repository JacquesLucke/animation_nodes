from . node_sorting import sortNodes
from . code_generator import getNodeExecutionLines
from . code_generator import PreparationScriptGenerator

class MainExecutionUnit:
    def __init__(self, network):
        self.network = network
        self.prepareScript = ""
        self.executeScript = ""
        self.prepareCodeObject = None
        self.executeCodeObject = None

        self.generateScripts()
        self.compileScripts()

    def generateScripts(self):
        nodes = self.network.getNodes()
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

    def execute(self):
        data = {}
        exec(self.prepareCodeObject, data, data)
        exec(self.executeCodeObject, data, data)
        data.clear()

def compileCode(script):
    return compile(script, "<string>", "exec")
