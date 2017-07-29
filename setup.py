import os
import re
import sys
import json

addonName = "animation_nodes"
currentDirectory = os.path.dirname(os.path.abspath(__file__))
addonsDirectory = os.path.join(currentDirectory, addonName)
assert os.path.isdir(addonsDirectory)

def main():
    logger = TaskLogger()
    setupInfoList = getSetupInfoList()
    execute_PyPreprocess(setupInfoList, logger)

def execute_PyPreprocess(setupInfoList, logger):
    tasks = getPyPreprocessTasks(setupInfoList)
    for task in tasks:
        logger.logExists(task)
        if task.dependenciesChanged():
            task.execute()
            logger.logExecuted(task)
            print("Updated:", task.target)

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


# Tasks
###########################################

class TaskLogger:
    def __init__(self):
        self.allTasks = []
        self.executedTasks = []

    def logExists(self, task):
        self.allTasks.append(task)

    def logExecuted(self, task):
        self.executedTasks.append(task)

class GenerateFileTask:
    def __init__(self, target, dependencies, function):
        self.target = target
        self.dependencies = dependencies
        self.function = function

    def execute(self):
        for path in self.dependencies:
            if not fileExists(path):
                raise Exception("file not found: " + path)

        self.function(self.target, Utils)

        if not fileExists(self.target):
            raise Exception("target has not been generated: " + self.target)

    def dependenciesChanged(self):
        return dependenciesChanged(self.target, self.dependencies)

    def __repr__(self):
        return "<{} for '{}' depends on '{}'>".format(
            type(self).__name__, self.target, self.dependencies)

class PyPreprocessTask(GenerateFileTask):
    pass


# Higher Level Utils
###########################################

def getSetupInfoList():
    setupInfoList = []
    for path in iterSetupInfoPaths():
        setupInfoList.append(executePythonFile(path))
    return setupInfoList

def iterSetupInfoPaths():
    return iterPathsWithFileName(addonsDirectory, "__setup_info.py")


# Utils
############################################

def executePythonFile(path):
    code = readTextFile(path)
    context = {"__file__" : path}
    exec(code, context)
    return context

def iterPathsWithFileName(basepath, filename):
    for root, dirs, files in os.walk(basepath):
        if filename in files:
            yield os.path.join(root, filename)

def readTextFile(path):
    with open(path, "rt") as f:
        return f.read()

def writeTextFile(path, content):
    with open(path, "wt") as f:
        f.write(content)

def readJsonFile(path):
    return json.loads(readTextFile(path))

def changeFileName(path, newName):
    return os.path.join(os.path.dirname(path), newName)

def filesExist(paths):
    assert all(fileExists(path) for path in paths)

def fileExists(path):
    return os.path.isfile(path)

def directoryExists(path):
    return os.path.isdir(path)

def dependenciesChanged(target, dependencies):
    targetTime = tryGetLastModificationTime(target)
    for path in dependencies:
        if tryGetLastModificationTime(path) > targetTime:
            return True
    return False

def tryGetLastModificationTime(path):
    try: return os.stat(path).st_mtime
    except: return 0

def multiReplace(text, **replacements):
    pattern = "|".join(re.escape(key) for key in replacements.keys())
    return re.sub(pattern, lambda m: replacements[m.group(0)], text)


class Utils:
    readTextFile = readTextFile
    writeTextFile = writeTextFile
    readJsonFile = readJsonFile
    changeFileName = changeFileName
    multiReplace = multiReplace


# Run Main
###############################################

main()
