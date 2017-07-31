import os
from . generic import *
from . task import GenerateFileTask

def execute_PyPreprocess(setupInfoList, logger, addonDirectory):
    printHeader("Run PyPreprocessor")

    tasks = getPyPreprocessTasks(setupInfoList)
    for task in tasks:
        logger.logPyPreprocessTask(task)
        task.execute()
        if task.targetChanged:
            print("Updated:", os.path.relpath(task.target, addonDirectory))

def getPyPreprocessTasks(setupInfoList):
    allTasks = []
    for path in getPyPreprocessorProviders(setupInfoList):
        allTasks.extend(getPyPreprocessTasksOfFile(path))
    return allTasks

def getPyPreprocessTasksOfFile(path):
    obj = executePythonFile(path)

    if "setup" in obj:
        obj["setup"](Utils)

    funcName = "getPyPreprocessTasks"
    if funcName not in obj:
        raise Exception("expected '{}' function in {}".format(funcName, path))

    tasks = obj[funcName](PyPreprocessTask, Utils)
    if not all(isinstance(p, PyPreprocessTask) for p in tasks):
        raise Exception("no list of {} objects returned".format(PyPreprocessTask.__name__))
    return tasks

def getPyPreprocessorProviders(setupInfoList):
    paths = []
    func = "getPyPreprocessorProviders"
    for info in setupInfoList:
        if func in info:
            for name in info[func]():
                path = changeFileName(info["__file__"], name)
                paths.append(path)
    return paths

class PyPreprocessTask(GenerateFileTask):
    def __init__(self, target, dependencies, function):
        super().__init__()
        self.target = target
        self.dependencies = dependencies
        self.function = function

    def execute(self):
        for path in self.dependencies:
            if not fileExists(path):
                raise Exception("file not found: " + path)

        if dependenciesChanged(self.target, self.dependencies):
            self.function(self.target, Utils)
            self.targetChanged = True

        if not fileExists(self.target):
            raise Exception("target has not been generated: " + self.target)

    def getSummary(self):
        return {
            "Target" : self.target,
            "Dependencies" : self.dependencies,
            "Changed" : self.targetChanged
        }

    def __repr__(self):
        return "<{} for '{}' depends on '{}'>".format(
            type(self).__name__, self.target, self.dependencies)

class Utils:
    readTextFile = readTextFile
    writeTextFile = writeTextFile
    readJsonFile = readJsonFile
    changeFileName = changeFileName
    multiReplace = multiReplace
