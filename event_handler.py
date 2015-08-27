from . utils.recursion import noRecursion
from . execution.units import setupExecutionUnits, finishExecutionUnits
from . execution.auto_execution import autoExecuteMainUnits, afterExecution
from . update import updateEverything
from . import problems

@noRecursion
def update(events):
    if events.intersection({"File", "Addon", "Tree"}):
        updateEverything()

    if problems.canAutoExecute():
        setupExecutionUnits()
        executed = autoExecuteMainUnits(events)
        if executed: afterExecution()
        finishExecutionUnits()
