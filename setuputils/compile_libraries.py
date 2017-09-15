from . generic import *

def execute_CompileLibraries(setupInfoList, logger, addonDirectory):
    printHeader("Compile Libraries")

    functionName = "getCompileLibraryTasks"
    for setupInfo in setupInfoList:
        if functionName in setupInfo:
            executeCompileLibraryTasks(setupInfo[functionName](Utils))

def executeCompileLibraryTasks(tasks):
    for task in tasks:
        task(Utils)
