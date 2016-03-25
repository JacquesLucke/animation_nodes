import bpy
from . utils.nodes import idToNode
from . utils.layout import writeText
from . tree_info import getNodeByIdentifier
from . utils.blender_ui import getDpiFactor

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


contactDeveloperMessage = (
    "Please contact a developer in the forum or on Github. "
    "If possible share your .blend file and the content of "
    "the console/terminal with the developer.")

realBugMessage = "This is most likely a bug in the addon itself. " + contactDeveloperMessage

advancedSettingsFixMessage = (
   "If you disabled certain problem-handling features in the "
   "advanced settings of the 'Expression' or 'Script' nodes "
   "try to enable them again.")

class NodeLinkRecursion(Problem):
    def allowExecution(self):
        return False

    def draw(self, layout):
        message = ("There is a cycle in your node tree. "
                   "You have to remove the cycle before you will "
                   "be able to execute the tree again.")
        writeText(layout, message, autoWidth = True)

class InvalidNetworksExist(Problem):
    def allowUnitCreation(self):
        return False

    def draw(self, layout):
        message = ("There is at least one invalid node network. "
                   "Please make all networks valid again.\n\n"
                   "Reasons for invalid networks:\n\n"
                   "  - a 'Invoke Subprogram' is in the same network that it calls\n\n"
                   "  - a 'Group Output' node has no corresponding 'Group Input' node\n\n"
                   "  - there are more than one 'Group Input', 'Group Output' or 'Loop Input' "
                       "nodes in the same network")
        writeText(layout, message, autoWidth = True)

class InvalidSyntax(Problem):
    def allowExecution(self):
        return False

    def draw(self, layout):
        message = "The execution code has invalid syntax.\n\n" + \
            realBugMessage + "\n\n" + advancedSettingsFixMessage
        writeText(layout, message, autoWidth = True)

class ExceptionDuringExecution(Problem):
    def allowExecution(self):
        return False

    def draw(self, layout):
        message = "An exception was raised during the execution of a node tree.\n\n" + \
            realBugMessage + "\n\n" + advancedSettingsFixMessage
        writeText(layout, message, autoWidth = True)

class ExceptionDuringCodeCreation(Problem):
    def allowExecution(self):
        return False

    def draw(self, layout):
        message = ("An exception was raised during the creation "
                   "of the execution code.\n\n") + realBugMessage
        writeText(layout, message, autoWidth = True)

class CouldNotSetupExecutionUnits(Problem):
    def allowExecution(self):
        return False

    def draw(self, layout):
        message = ("The Animation Nodes addon is not able to setup "
                   "the execution units for your node tree.\n\n") + realBugMessage
        writeText(layout, message, autoWidth = True)

class NodeFailesToCreateExecutionCode(Problem):
    def __init__(self, nodeIdentifier):
        self.nodeIdentifier = nodeIdentifier

    def allowUnitCreation(self):
        return False

    def draw(self, layout):
        message = ("The node linked below is not able to create its "
                   "execution code. If this can happen when the node tree "
                   "has been created in another version of the addon. If that "
                   "is not the case it is most likely a bug in the addon itself.\n\n") + \
                   contactDeveloperMessage + "\n\n" + \
                  ("If the problem is that you use an incompatible AN version, you "
                   "can also try to simply replace the not-working node with the same node. "
                   "Sometimes this error occures when the sockets of a node changes "
                   "between versions.")
        writeText(layout, message, autoWidth = True)

        node = getNodeByIdentifier(self.nodeIdentifier)
        props = layout.operator("an.move_view_to_node", icon = "VIEWZOOM", text = "{} does not work".format(repr(node.name)))
        props.nodeIdentifier = self.nodeIdentifier

class NodeShouldNotBeUsedInAutoExecution(Problem):
    def __init__(self, nodeIdentifier):
        self.nodeIdentifier = nodeIdentifier

    def allowAutoExecution(self):
        return False

    def draw(self, layout):
        node = getNodeByIdentifier(self.nodeIdentifier)
        layout.label("{} should not be used with auto execution.".format(repr(node.name)))

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
        writeText(col, message, autoWidth = True)
        col.operator("an.replace_nodes_with_copies")

class LinkedAnimationNodeTreeExists(Problem):
    def allowUnitCreation(self):
        return False

    def draw(self, layout):
        layout.label("AN doesn't support linked node trees.")

class UndefinedNodeExists(Problem):
    def __init__(self, nodes):
        self.nodeIDs = [node.toID() for node in nodes]

    def allowUnitCreation(self):
        return False

    def draw(self, layout):
        message = ("There is at least one undefined node. "
                   "This happens when you open a .blend file uses "
                   "nodes which don't exist in your version of AN.\n"
                   "To fix this you can either install the AN version this "
                   "file has been created with or you try to replace/remove "
                   "the undefined nodes.")

        writeText(layout, message, autoWidth = True)

        col = layout.column(align = True)
        for nodeID in self.nodeIDs:
            node = idToNode(nodeID)
            props = col.operator("an.move_view_to_node", icon = "VIEWZOOM", text = "{} is undefined".format(repr(node.name)))
            props.treeName = nodeID[0]
            props.nodeName = nodeID[1]




# Exceptions
########################################

class ExecutionUnitNotSetup(Exception):
    pass
