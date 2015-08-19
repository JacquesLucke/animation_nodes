import os
from collections import defaultdict
from . utils.timing import measureTime

addonName = os.path.basename(os.path.dirname(__file__))

def generateCode(network):
    coder = CodeGenerator(network)
    return coder.generatePreparationScript(), coder.generateExecutionScript()

# Sorting
###############################

def sortNodes(nodes):
    preSort = []
    for node in nodes:
        preSort.extend(getAllDependencies(node))
        preSort.append(node)
    return removeDuplicates(preSort)

def removeDuplicates(elements):
    seen = set()
    see = seen.add
    return [element for element in elements if not(element in seen or see(element))]

def getAllDependencies(node, recursionStart = None):
    dependencies = []
    dataOrigins = node.originNodes
    for dataOrigin in dataOrigins:
        if dataOrigin == recursionStart: raise NodeRecursionDetected()
        dependencies.extend(getAllDependencies(dataOrigin, recursionStart = node))
    dependencies.extend(dataOrigins)
    return dependencies

class NodeRecursionDetected(Exception):
    pass


# Stuff
#########################

class CodeGenerator:
    def __init__(self, network):
        self.network = network
        self.nodes = sortNodes(network.getAnimationNodes())
        self.socketVariables = defaultdict()

    def generatePreparationScript(self):
        lines = []
        add = lines.append
        extend = lines.extend
        add(self.getImportStatement())
        add("animation_nodes = sys.modules[{}]".format(repr(addonName)))
        add("")
        add("scene = bpy.context.scene")
        add("nodes = bpy.data.node_groups[{}].nodes".format(repr(self.network.treeName)))
        add("")
        for node in self.nodes:
            add("{} = nodes[{}]".format(node.identifier, repr(node.name)))
            for socket in node.unlinkedInputs:
                self.generateSocketVariable(socket)
                add("{} = {}.inputs[{}].getValue()".format(self.socketVariables[socket], node.identifier, socket.index))
            add("")
        return "\n".join(lines)

    def generateExecutionScript(self):
        lines = self.getMainLines()
        return "\n".join(lines)

    def getImportStatement(self):
        neededModules = {"bpy", "sys"}
        neededModules.update(self.getModulesNeededByNodes())
        return "import " + ", ".join(neededModules)

    def getModulesNeededByNodes(self):
        moduleNames = set()
        for node in self.nodes:
            moduleNames.update(node.getModuleList())
        return list(moduleNames)

    def getMainLines(self):
        lines = []
        for node in self.nodes:
            lines.extend(self.getNodeLines(node))
        return lines

    def getNodeLines(self, node):
        lines = node.getTaggedExecutionCodeLines()
        lines = [self.replaceTaggedLine(line, node) for line in lines]
        for socket in node.linkedOutputs:
            for target in socket.dataTargetSockets:
                self.socketVariables[target] = self.socketVariables[socket]
        return lines

    def replaceTaggedLine(self, line, node):
        line = line.replace("#self#", node.identifier)
        for name, identifier in node.inputNames.items():
            line = line.replace("%{}%".format(identifier), self.socketVariables[node.inputsByIdentifier[name]])
        for name, identifier in node.outputNames.items():
            socket = node.outputsByIdentifier[name]
            self.generateSocketVariable(socket)
            line = line.replace("${}$".format(identifier), self.socketVariables[socket])
        return line

    def generateSocketVariable(self, socket):
        self.socketVariables[socket] = "_{}{}".format(socket.identifier, socket.node.identifier[:3])

def indent(lines):
    return ["    " + line for line in lines]
