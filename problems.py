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
    def __init__(self, networks):
        self.networks = networks

    def allowUnitCreation(self):
        return False

    def draw(self, layout):
        layout.label("At least one invalid network exists")

class InvalidSyntax(Problem):
    def __init__(self, code):
        self.code = code

    def allowExecution(self):
        return False

    def draw(self, layout):
        row = layout.row()
        row.label("Invalid Syntax")
        props = row.operator("an.print_text", text = "Print")
        props.text = self.code
        props.emptyLines = 5

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

    def allowAutoExecution(self, layout):
        return False

    def draw(self, layout):
        layout.label("A node should not be used with auto execution")

class NodeMustNotBeInSubprogram(Problem):
    def __init__(self, nodeIdentifier):
        self.nodeIdentifier = nodeIdentifier

    def allowUnitCreation(self):
        return False

    def draw(self, layout):
        layout.label("A node must not be in a subprogram")

class NodeDoesNotSupportExecution(Problem):
    def __init__(self, nodeIdentifier):
        self.nodeIdentifier = nodeIdentifier

    def allowUnitCreation(self):
        return False

    def draw(self, layout):
        layout.label("A node does not support excecution")




# Exceptions
########################################

class ExecutionUnitNotSetup(Exception):
    pass
