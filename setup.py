import os
import re
import io
import sys
import json
import glob
import contextlib

addonName = "animation_nodes"
currentDirectory = os.path.dirname(os.path.abspath(__file__))
addonDirectory = os.path.join(currentDirectory, addonName)
summaryPath = os.path.join(currentDirectory, "setup_summary.json")
assert os.path.isdir(addonDirectory)

def main():
    logger = TaskLogger()
    setupInfoList = getSetupInfoList()
    execute_PyPreprocess(setupInfoList, logger)
    execute_Cythonize(setupInfoList, logger)
    execute_Compile(setupInfoList, logger)
    execute_PrintSummary(logger)
    execute_SaveSummary(logger)


# PyProprocess
###########################################

def execute_PyPreprocess(setupInfoList, logger):
    printHeader("Run PyPreprocessor")

    tasks = getPyPreprocessTasks(setupInfoList)
    logger.pyPreprocessTasks = tasks
    for task in tasks:
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


# Cythonize
###########################################

def execute_Cythonize(setupInfoList, logger):
    printHeader("Run Cythonize")
    tasks = getCythonizeTasks()
    logger.cythonizeTasks = tasks
    for task in tasks:
        task.execute()

def getCythonizeTasks():
    tasks = []
    for path in iterCythonFilePaths():
        tasks.append(CythonizeTask(path))
    return tasks

def iterCythonFilePaths():
    yield from iterPathsWithExtension(addonDirectory, ".pyx")


# Compile
###########################################

def execute_Compile(setupInfoList, logger):
    printHeader("Compile")
    tasks = getCompileTasks(logger.getFilesGeneratedByCython())
    logger.compilationTasks = tasks
    for task in tasks:
        task.execute()

def getCompileTasks(filesToCompile):
    tasks = []
    for path in filesToCompile:
        tasks.append(CompileExtModuleTask(path))
    return tasks


# Summary
###########################################

def execute_PrintSummary(logger):
    printHeader("Summary")

    changedPaths = logger.getModifiedPaths()
    for path in changedPaths:
        print("Changed: " + os.path.relpath(path, currentDirectory))

    print("\n{} files changed".format(len(changedPaths)))


# Save Summary
###########################################

def execute_SaveSummary(logger):
    summary = getSummary(logger)
    writeJsonFile(summaryPath, summary)

def getSummary(logger):
    return {
        "PyPreprocess" : getPyPreprocessSummary(logger),
        "Cythonize" : getCythonizeSummary(logger),
        "Compilation" : getCompilationSummary(logger)
    }

def getPyPreprocessSummary(logger):
    return [task.getSummary() for task in logger.pyPreprocessTasks]

def getCythonizeSummary(logger):
    return [task.getSummary() for task in logger.cythonizeTasks]

def getCompilationSummary(logger):
    return [task.getSummary() for task in logger.compilationTasks]


# Tasks
###########################################

class TaskLogger:
    def __init__(self):
        self.pyPreprocessTasks = []
        self.cythonizeTasks = []
        self.compilationTasks = []

    def getAllTasks(self):
        return self.pyPreprocessTasks + self.cythonizeTasks + self.compilationTasks

    def getModifiedPaths(self):
        paths = []
        for task in self.getAllTasks():
            if task.targetChanged:
                paths.append(task.target)
        return paths

    def getFilesGeneratedByCython(self):
        return [task.target for task in self.cythonizeTasks]

class GenerateFileTask:
    def __init__(self):
        self.target = None
        self.targetChanged = False

    def getSummary(self):
        return None

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

class CythonizeTask(GenerateFileTask):
    def __init__(self, path):
        super().__init__()
        self.path = path
        self.target = changeFileExtension(path, ".c")

    def execute(self):
        from Cython.Build import cythonize

        timeBefore = tryGetLastModificationTime(self.target)
        cythonize(self.path)
        timeAfter = tryGetLastModificationTime(self.target)

        if not fileExists(self.target):
            raise Exception("target has not been generated: " + self.target)

        if timeAfter > timeBefore:
            self.targetChanged = True

    def getSummary(self):
        return {
            "Path" : self.path,
            "Target" : self.target,
            "Changed" : self.targetChanged
        }

    def __repr__(self):
        return "<{} for '{}'>".format(type(self).__name__, self.target)

class CompileExtModuleTask(GenerateFileTask):
    def __init__(self, path):
        super().__init__()
        self.path = path
        self.target = None

    def execute(self):
        extension = getExtensionFromPath(self.path)
        targetsBefore = getPossibleCompiledFilesWithTime(self.path)
        buildExtensionInplace(extension)
        targetsAfter = getPossibleCompiledFilesWithTime(self.path)
        newTargets = set(targetsAfter) - set(targetsBefore)

        if len(targetsAfter) == 0:
            raise Exception("target has not been generated for " + self.path)
        elif len(newTargets) == 0:
            self.target = max(targetsAfter, key = lambda x: x[1])[0]
        elif len(newTargets) == 1:
            self.target = newTargets.pop()[0]
            self.targetChanged = True
        else:
            raise Exception("cannot choose the correct target for " + self.path)

    def getSummary(self):
        return {
            "Path" : self.path,
            "Target" : self.target,
            "Changed" : self.targetChanged
        }

def getPossibleCompiledFilesWithTime(cpath):
    directory = os.path.dirname(cpath)
    name = getFileNameWithoutExtension(cpath)
    pattern = os.path.join(directory, name) + ".*"
    paths = glob.glob(pattern + ".pyd") + glob.glob(pattern + ".so")
    return [(path, tryGetLastModificationTime(path)) for path in paths]

def getExtensionFromPath(path):
    from distutils.core import Extension
    metadata = getCythonMetadata(path)
    return Extension(metadata["module_name"], [path])

def buildExtensionInplace(extension):
    from distutils.core import setup
    oldArgs = sys.argv
    sys.argv = [oldArgs[0], "build_ext", "--inplace"]
    setup(ext_modules = [extension])
    sys.argv = oldArgs


# Higher Level Utils
###########################################

def getSetupInfoList():
    setupInfoList = []
    for path in iterSetupInfoPaths():
        setupInfoList.append(executePythonFile(path))
    return setupInfoList

def iterSetupInfoPaths():
    return iterPathsWithFileName(addonDirectory, "__setup_info.py")

def getCythonMetadata(path):
    text = readLinesBetween(path, "BEGIN: Cython Metadata", "END: Cython Metadata")
    return json.loads(text)


# Utils
############################################

def printHeader(text):
    print()
    print()
    print(text)
    print("-"*50)
    print()

def executePythonFile(path):
    code = readTextFile(path)
    context = {"__file__" : path}
    exec(code, context)
    return context

def iterPathsWithExtension(basepath, extension):
    for root, dirs, files in os.walk(basepath):
        for filename in files:
            _, ext = os.path.splitext(filename)
            if ext == extension:
                yield os.path.join(root, filename)

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

def writeJsonFile(path, content):
    writeTextFile(path, json.dumps(content, sort_keys = True, indent = 4))

def changeFileName(path, newName):
    return os.path.join(os.path.dirname(path), newName)

def changeFileExtension(path, newExtension):
    return os.path.splitext(path)[0] + newExtension

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

def getNewestPath(paths):
    pathsWithTime = [(path, tryGetLastModificationTime(path)) for path in paths]
    return max(pathsWithTime, key = lambda x: x[1])[0]

def tryGetLastModificationTime(path):
    try: return os.stat(path).st_mtime
    except: return 0

def getFileNameWithoutExtension(path):
    return os.path.basename(os.path.splitext(path)[0])

def multiReplace(text, **replacements):
    pattern = "|".join(re.escape(key) for key in replacements.keys())
    return re.sub(pattern, lambda m: replacements[m.group(0)], text)

def readLinesBetween(path, start, stop):
    lines = []
    with open(path, "rt") as f:
        while True:
            line = f.readline()
            if line == "":
                raise Exception("Line containing '{}' not found".format(start))
            if start in line:
                break

        while True:
            line = f.readline()
            if line == "":
                raise Exception("Line containing '{}' not found".format(stop))
            if stop not in line:
                lines.append(line)
            else:
                break
    return "".join(lines)


class Utils:
    readTextFile = readTextFile
    writeTextFile = writeTextFile
    readJsonFile = readJsonFile
    changeFileName = changeFileName
    multiReplace = multiReplace


# Run Main
###############################################

main()
