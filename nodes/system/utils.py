from ... tree_info import getNodesByType

def updateCallerNodes(identifier):
    for node in getCallerNodesForSubprogram(identifier):
        node.updateSockets()

def getCallerNodesForSubprogram(identifier):
    callerNodes = getNodesByType("an_SubprogramCaller")
    return [node for node in callerNodes if node.subprogramIdentifier == identifier]
