from .. utils.nodes import getAnimationNodeTrees

def autoExecuteMainUnits(events):
    for nodeTree in getAnimationNodeTrees():
        if nodeTree.canAutoExecute(events):
            nodeTree.execute()
