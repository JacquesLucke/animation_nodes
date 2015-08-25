from ... tree_info import getNodesByType

def updateCallerNodes():
    for node in getNodesByType("an_SubprogramCaller"):
        node.updateSockets()
