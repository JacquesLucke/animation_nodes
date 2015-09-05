from ... import tree_info

def _updateSubprogramInvokerNodes():
    tree_info.updateIfNecessary()
    for node in tree_info.getNodesByType("an_InvokeSubprogramNode"):
        node.updateSockets()
    tree_info.updateIfNecessary()


subprogramChanged = False

def updateIfNecessary():
    global subprogramChanged
    if subprogramChanged: _updateSubprogramInvokerNodes()
    subprogramChanged = False

def subprogramInterfaceChanged():
    from ... events import treeChanged
    global subprogramChanged
    subprogramChanged = True
    treeChanged()
