from collections import defaultdict
from .. tree_info import getNetworksByType
from . main_execution_unit import MainExecutionUnit

_mainUnitsByNodeTree = defaultdict(list)

def createExecutionUnits():
    reset()
    createMainUnits()

def reset():
    _mainUnitsByNodeTree.clear()

def createMainUnits():
    for network in getNetworksByType("Main"):
        unit = MainExecutionUnit(network)
        _mainUnitsByNodeTree[network.treeName].append(unit)


def getMainUnitsByNodeTree(nodeTree):
    return _mainUnitsByNodeTree[nodeTree.name]
