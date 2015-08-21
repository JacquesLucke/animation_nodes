import os
from collections import defaultdict

class PreparationScriptGenerator:
    def __init__(self, nodes):
        self.nodes = nodes
        self.script = ""
        self.socketVariables = defaultdict()

    def generate(self):
        lines = []
        add = lines.append
        extend = lines.extend

        add(self.getImportStatement())
        add("")
        add("scene = bpy.context.scene")
        add("nodes = bpy.data.node_groups[{}].nodes".format(repr(self.nodes[0].nodeTree.name)))
        add("")
        extend(self.getNodePreparationLines())

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

    def getNodePreparationLines(self):
        lines = []
        for node in self.nodes:
            lines.append(self.getNodePreparationLine(node))
            lines.extend(self.getInputsPreparationLines(node))
            lines.append("")
        return lines

    def getNodePreparationLine(self, node):
        return "{} = nodes[{}]".format(node.identifier, repr(node.name))

    def getInputsPreparationLines(self, node):
        lines = []
        for socket in node.unlinkedInputs:
            self.generateSocketVariable(socket)
            lines.append("{} = {}.inputs[{}].getValue()".format(
                self.socketVariables[socket], node.identifier, socket.index))
        return lines

    def generateSocketVariable(self, socket):
        insertSocketVariable(self.socketVariables, socket)


def getNodeExecutionLines(node, socketVariables):
    lines = node.getTaggedExecutionCodeLines()
    lines = [replaceTaggedLine(line, node, socketVariables) for line in lines]
    linkAllTargetSocketVariables(node, socketVariables)
    return lines

def replaceTaggedLine(line, node, socketVariables):
    line = line.replace("#self#", node.identifier)
    for name, identifier in node.inputNames.items():
        line = line.replace("%{}%".format(identifier), socketVariables[node.inputsByIdentifier[name]])
    for name, identifier in node.outputNames.items():
        socket = node.outputsByIdentifier[name]
        insertSocketVariable(socketVariables, socket)
        line = line.replace("${}$".format(identifier), socketVariables[socket])
    return line

def linkAllTargetSocketVariables(node, socketVariables):
    for socket in node.linkedOutputs:
        linkTargetSocketVariables(socket, socketVariables)

def linkTargetSocketVariables(socket, socketVariables):
    for target in socket.dataTargetSockets:
        socketVariables[target] = socketVariables[socket]

def insertSocketVariable(socketVariables, socket):
    socketID = socket.identifier if socket.identifier.isidentifier() else "_socket_{}_{}".format(socket.isOutput, socket.index)
    variable = "_{}{}".format(socketID, socket.node.identifier[:4])
    socketVariables[socket] = variable
