import traceback
from .. problems import ExceptionDuringCodeCreation, CouldNotSetupExecutionUnits
from .. import problems
from collections import defaultdict
from . cache import clearExecutionCache
from . main_execution_unit import MainExecutionUnit
from . group_execution_unit import GroupExecutionUnit
from . loop_execution_unit import LoopExecutionUnit
from . script_execution_unit import ScriptExecutionUnit
from .. tree_info import getNetworksByType, getSubprogramNetworks
from .. utils.timing import measureTime

_mainUnitsByNodeTree = defaultdict(list)
_subprogramUnitsByIdentifier = {}

@measureTime
def createExecutionUnits():
    reset()
    try:
        createMainUnits()
        createSubprogramUnits()
    except:
        print("\n"*5)
        traceback.print_exc()
        ExceptionDuringCodeCreation().report()

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
        if network.type == "Loop":
            unit = LoopExecutionUnit(network)
        if network.type == "Script":
            unit = ScriptExecutionUnit(network)
        _subprogramUnitsByIdentifier[network.identifier] = unit


def setupExecutionUnits():
    try:
        if not problems.canExecute(): return

        for unit in getExecutionUnits():
            unit.setup()

        subprograms = {}
        for identifier, unit in _subprogramUnitsByIdentifier.items():
            subprograms["_subprogram" + identifier] = unit.execute

        for unit in getExecutionUnits():
            unit.insertSubprogramFunctions(subprograms)
    except:
        print("\n"*5)
        traceback.print_exc()
        CouldNotSetupExecutionUnits().report()

def finishExecutionUnits():
    for unit in getExecutionUnits():
        unit.finish()

    clearExecutionCache()


def getMainUnitsByNodeTree(nodeTree):
    return _mainUnitsByNodeTree[nodeTree.name]

def getSubprogramUnitByIdentifier(identifier):
    return _subprogramUnitsByIdentifier.get(identifier)

def getSubprogramUnitsByName(name):
    programs = []
    for subprogram in _subprogramUnitsByIdentifier.values():
        if subprogram.network.name == name:
            programs.append(subprogram)
    return programs

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
