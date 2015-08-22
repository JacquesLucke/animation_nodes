from collections import defaultdict
from . main_execution_unit import MainExecutionUnit
from . group_execution_unit import GroupExecutionUnit
from .. tree_info import getNetworksByType, getSubprogramNetworks
from .. import problems

_mainUnitsByNodeTree = defaultdict(list)
_subprogramUnitsByIdentifier = {}

def createExecutionUnits():
    reset()
    createMainUnits()
    createSubprogramUnits()

def reset():
    _mainUnitsByNodeTree.clear()
    _subprogramUnitsByIdentifier.clear()

def createMainUnits():
    for network in getNetworksByType("Main"):
        unit = MainExecutionUnit(network)
        _mainUnitsByNodeTree[network.treeName].append(unit)

def createSubprogramUnits():
    for network in getSubprogramNetworks():
        if network.type == "Group":
            unit = GroupExecutionUnit(network)
        _subprogramUnitsByIdentifier[network.identifier] = unit



def setupExecutionUnits():
    if not problems.canExecute(): return

    for unit in getExecutionUnits():
        unit.setup()

    subprograms = {}
    for identifier, unit in _subprogramUnitsByIdentifier.items():
        subprograms["_subprogram" + identifier] = unit.execute

    for unit in getExecutionUnits():
        unit.insertSubprogramFunctions(subprograms)

def finishExecutionUnits():
    for unit in getExecutionUnits():
        unit.finish()


def getMainUnitsByNodeTree(nodeTree):
    return _mainUnitsByNodeTree[nodeTree.name]

def getSubprogramUnitByIdentifier(identifier):
    return _subprogramUnitsByIdentifier.get(identifier)

def getExecutionUnitByNetwork(network):
    for unit in getExecutionUnits():
        if unit.network == network: return unit

def getExecutionUnits():
    units = []
    for mainUnits in _mainUnitsByNodeTree.values():
        units.extend(mainUnits)
    for subprogramUnit in _subprogramUnitsByIdentifier.values():
        units.append(subprogramUnit)
    return units
