from . utils.layout import writeText
from . tree_info import getNodeByIdentifier

currentProblems = []

def reset():
    currentProblems.clear()

def canCreateExecutionUnits():
    for problem in currentProblems:
        if not problem.allowUnitCreation(): return False
    return True

def canExecute():
    for problem in currentProblems:
        if not problem.allowExecution(): return False
    return True

def canAutoExecute():
    for problem in currentProblems:
        if not problem.allowAutoExecution(): return False
    return True

def getProblems():
    return currentProblems


class Problem:
    def allowUnitCreation(self):
        return True

    def allowExecution(self):
        return self.allowUnitCreation()

    def allowAutoExecution(self):
        return self.allowExecution()

    def draw(self, layout):
        pass

    def report(self):
        currentProblems.append(self)


class NodeLinkRecursion(Problem):
    def allowExecution(self):
        return False

    def draw(self, layout):
        layout.label("Node Recursion")

class InvalidNetworksExist(Problem):
    def allowUnitCreation(self):
        return False

    def draw(self, layout):
        layout.label("At least one invalid network exists")

class InvalidSyntax(Problem):
    def allowExecution(self):
        return False

    def draw(self, layout):
        layout.label("Invalid Syntax (see console)")

class ExceptionDuringExecution(Problem):
    def allowExecution(self):
        return False

    def draw(self, layout):
        layout.label("Exception during execution (see console)")

class ExceptionDuringCodeCreation(Problem):
    def allowExecution(self):
        return False

    def draw(self, layout):
        layout.label("Exception during code creation (see console)")

class CouldNotSetupExecutionUnits(Problem):
    def allowExecution(self):
        return False

    def draw(self, layout):
        layout.label("Could not setup execution units (see console)")

class NodeFailesToCreateExecutionCode(Problem):
    def __init__(self, nodeIdentifier):
        self.nodeIdentifier = nodeIdentifier

    def allowUnitCreation(self):
        return False

    def draw(self, layout):
        node = getNodeByIdentifier(self.nodeIdentifier)
        props = layout.operator("an.move_view_to_node", text = "{} Needs Update".format(repr(node.name)))
        props.nodeIdentifier = self.nodeIdentifier

class SubprogramInvokesItself(Problem):
    def __init__(self, network):
        self.network = network

    def allowUnitCreation(self):
        return False

    def draw(self, layout):
        layout.label("{} invokes itself".format(repr(self.network.name)))

class NodeShouldNotBeUsedInAutoExecution(Problem):
    def __init__(self, nodeIdentifier):
        self.nodeIdentifier = nodeIdentifier

    def allowAutoExecution(self):
        return False

    def draw(self, layout):
        node = getNodeByIdentifier(self.nodeIdentifier)
        layout.label("{} should not be used with auto execution".format(repr(node.name)))

class NodeMustNotBeInSubprogram(Problem):
    def __init__(self, nodeIdentifier):
        self.nodeIdentifier = nodeIdentifier

    def allowUnitCreation(self):
        return False

    def draw(self, layout):
        node = getNodeByIdentifier(self.nodeIdentifier)
        layout.label("{} must not be in a subprogram".format(repr(node.name)))

class NodeDoesNotSupportExecution(Problem):
    def __init__(self, nodeIdentifier):
        self.nodeIdentifier = nodeIdentifier

    def allowUnitCreation(self):
        return False

    def draw(self, layout):
        node = getNodeByIdentifier(self.nodeIdentifier)
        layout.label("{} does not support excecution".format(repr(node.name)))

class IdentifierExistsTwice(Problem):
    def allowUnitCreation(self):
        return False

    def draw(self, layout):
        message = ("At least one node identifier exists twice. "
                   "This can happen when you append a node tree "
                   "that is already in this file. \n"
                   "Solution: \n"
                   "  1. Select the NEW node tree \n"
                   "  2. Click on the button below")
        col = layout.column()
        writeText(col, message)
        col.operator("an.replace_nodes_with_copies")





# Exceptions
########################################

class ExecutionUnitNotSetup(Exception):
    pass
