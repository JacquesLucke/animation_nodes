import traceback
from .. import problems
from collections import defaultdict
from . cache import clearExecutionCache
from . measurements import resetMeasurements
from . main_execution_unit import MainExecutionUnit
from . loop_execution_unit import LoopExecutionUnit
from . group_execution_unit import GroupExecutionUnit
from . script_execution_unit import ScriptExecutionUnit
from .. utils.nodes import getAnimationNodeTrees, iterAnimationNodes
from .. problems import ExceptionDuringCodeCreation, CouldNotSetupExecutionUnits
from .. tree_info import getNetworksByType, getSubprogramNetworks, getNetworkByIdentifier

_mainUnitsByNodeTree = defaultdict(list)
_subprogramUnitsByIdentifier = {}

def createExecutionUnits(nodeByID):
    reset()
    try:
        createMainUnits(nodeByID)
        createSubprogramUnits(nodeByID)
    except:
        print("\n"*5)
        traceback.print_exc()
        ExceptionDuringCodeCreation().report()

def reset():
    resetMeasurements()
    _mainUnitsByNodeTree.clear()
    _subprogramUnitsByIdentifier.clear()

    for node in iterAnimationNodes():
        for socket in node.outputs:
            socket.execution.neededCopies = 0

def createMainUnits(nodeByID):
    for network in getNetworksByType("Main"):
        unit = MainExecutionUnit(network, nodeByID)
        _mainUnitsByNodeTree[network.treeName].append(unit)

def createSubprogramUnits(nodeByID):
    for network in getSubprogramNetworks():
        if network.type == "Group":
            unit = GroupExecutionUnit(network, nodeByID)
        if network.type == "Loop":
            unit = LoopExecutionUnit(network, nodeByID)
        if network.type == "Script":
            unit = ScriptExecutionUnit(network, nodeByID)
        _subprogramUnitsByIdentifier[network.identifier] = unit


def setupExecutionUnits(nodeTrees):
    try:
        if len(nodeTrees) == 0: return
        if not problems.canExecute(): return

        executionUnits = getExecutionUnits(nodeTrees)

        for unit in executionUnits:
            unit.setup()

        subprograms = {}
        for identifier, unit in _subprogramUnitsByIdentifier.items():
            subprograms["_subprogram" + identifier] = unit.execute

        for unit in executionUnits:
            unit.insertSubprogramFunctions(subprograms)
    except:
        print("\n"*5)
        traceback.print_exc()
        CouldNotSetupExecutionUnits().report()

def finishExecutionUnits(nodeTrees):
    for unit in getExecutionUnits(nodeTrees):
        unit.finish()

    clearExecutionCache()


def getMainUnitsByNodeTree(nodeTree):
    return _mainUnitsByNodeTree[nodeTree.name]

def getSubprogramUnitByIdentifier(identifier):
    return _subprogramUnitsByIdentifier.get(identifier, None)

def getSubprogramUnitsByName(name):
    programs = []
    for subprogram in _subprogramUnitsByIdentifier.values():
        if subprogram.network.name == name:
            programs.append(subprogram)
    return programs

def getExecutionUnitByNetwork(network):
    for unit in getExecutionUnits([network.nodeTree]):
        if unit.network == network: return unit

def getExecutionUnits(nodeTrees):
    units = []
    for nodeTree in nodeTrees:
        units.extend(_mainUnitsByNodeTree[nodeTree.name])

        for network in nodeTree.networks:
            for subprogramID in getNeededSubprogramIDs(network):
                units.append(_subprogramUnitsByIdentifier[subprogramID])
    return units

def getNeededSubprogramIDs(network):
    subprogramIDs = network.referencedSubprogramIDs.copy()
    for subprogramID in network.referencedSubprogramIDs:
        subNetwork = getNetworkByIdentifier(subprogramID)
        subprogramIDs.update(getNeededSubprogramIDs(subNetwork))
    return subprogramIDs
