from ... import tree_info
from ... events import executionCodeChanged

def updateSubprogramInvokerNodes():
    tree_info.update()
    for node in tree_info.getNodesByType("an_InvokeSubprogramNode"):
        node.updateSockets()
    executionCodeChanged()
