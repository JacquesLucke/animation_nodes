from . utils.recursion import noRecursion
from . execution.units import setupExecutionUnits, finishExecutionUnits
from . execution.auto_execution import autoExecuteMainUnits, afterExecution
from . update import updateEverything

@noRecursion
def update(events):
    if events.intersection({"File", "Addon", "Tree"}):
        updateEverything()

    setupExecutionUnits()
    executed = autoExecuteMainUnits(events)
    if executed: afterExecution()
    finishExecutionUnits()
