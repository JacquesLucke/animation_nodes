from ... tree_info import getNodesByType

def updateSubprogramInvokerNodes():
    for node in getNodesByType("an_InvokeSubprogramNode"):
        node.updateSockets()
