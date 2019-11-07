import os
from . generic import *

def execute_PyPreprocess(setupInfoList, addonDirectory):
    printHeader("Run PyPreprocessor")

    tasks = getPyPreprocessTasks(setupInfoList)
    for i, task in enumerate(tasks):
        relativePath = os.path.relpath(task.target, addonDirectory)
        print("{}/{}: {}".format(i+1, len(tasks), relativePath))
        task.execute()

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

class PyPreprocessTask:
    def __init__(self, target, dependencies, function):
        self.target = target
        self.dependencies = dependencies
        self.function = function

    def execute(self):
        for path in self.dependencies:
            if not fileExists(path):
                raise Exception("file not found: " + path)

        if dependenciesChanged(self.target, self.dependencies):
            self.function(self.target, Utils)

        if not fileExists(self.target):
            raise Exception("target has not been generated: " + self.target)

    def __repr__(self):
        return "<{} for '{}' depends on '{}'>".format(
            type(self).__name__, self.target, self.dependencies)
