import os
import re
import io
import sys
import stat
import json
import glob
import shutil
import textwrap
import contextlib

addonName = "animation_nodes"
currentDirectory = os.path.dirname(os.path.abspath(__file__))
addonDirectory = os.path.join(currentDirectory, addonName)
summaryPath = os.path.join(currentDirectory, "setup_summary.json")
defaultConfigPath = os.path.join(currentDirectory, "conf.default.json")
configPath = os.path.join(currentDirectory, "conf.json")
assert os.path.isdir(addonDirectory)

class SetupOptions:
    def __init__(self):
        self.cythonize = True
        self.compile = True
        self.force = False
        self.copy = False
        self.exportFull = False
        self.exportC = False

setupOptions = SetupOptions()

possibleCommands = ["build", "clean", "help"]

buildOptionDescriptions = [
    ("--copy", "Copy build to location specified in the conf.json file"),
    ("--force", "Rebuild everything"),
    ("--export", "Create installable .zip file"),
    ("--exportc", "Create build that can be compiled without cython"),
    ("--nocompile", "Don't compile the extension modules"),
    ("--noversioncheck", "Don't check the used Python version")
]
buildOptions = {option for option, _ in buildOptionDescriptions}
helpNote = "Use 'python setup.py help' to see the possible commands."

def main():
    configs = setupConfigFile()
    print(configs)
    args = sys.argv[1:]
    if len(args) == 0 or args[0] == "help":
        main_Help()
    elif args[0] == "build":
        main_Build(args[1:])
    elif args[0] == "clean":
        main_Clean()
    else:
        print("Invalid command: '{}'\n".format(args[0]))
        print(helpNote)
        sys.exit()

def setupConfigFile():
    if not fileExists(defaultConfigPath):
        print("Expected conf.default.json file to exist.")
        sys.exit()
    if not fileExists(configPath):
        copyFile(defaultConfigPath, configPath)
        print(textwrap.dedent('''\
        Copied the conf.default.json file to conf.json.
        Please change it manually if needed.
        Note: git ignorers it, so depending on the settings of your editor
              it might not be shows inside it.
        '''))
    return readJsonFile(configPath)

def main_Help():
    print(textwrap.dedent('''\
    usage: python setup.py <command> [options]

    Possible commands:
        help                Show this help
        build               Build the addon from sources
        clean               Remove generated files

    The 'build' command has multiple options:'''))
    for option, description in buildOptionDescriptions:
        print("    {:20}{}".format(option, description))
    sys.exit()

def main_Build(options):
    checkBuildEnvironment(
        checkCython = True,
        checkPython = "--noversioncheck" not in options
    )
    checkBuildOptions(options)

    logger = TaskLogger()
    setupInfoList = getSetupInfoList()
    execute_PyPreprocess(setupInfoList, logger)
    execute_Cythonize(setupInfoList, logger)
    if "--nocompile" not in options:
        execute_Compile(setupInfoList, logger)
    if "--copy" in options:
        execute_CopyAddon(logger)
    execute_PrintSummary(logger)
    execute_SaveSummary(logger)
    print("Let's build")

def checkBuildEnvironment(checkCython, checkPython):
    if checkCython:
        try: import Cython
        except:
            print("Cython is not installed for this Python version.")
            print(sys.version)
            sys.exit()
    if checkPython:
        v = sys.version_info
        if v.major != 3 or v.minor != 5:
            print(textwrap.dedent('''\
            Blender 2.78/2.79 officially uses Python 3.5.x.
            You are using: {}

            Use the --noversioncheck option to disable this check.\
            '''.format(sys.version)))
            sys.exit()

def checkBuildOptions(options):
    options = set(options)
    invalidOptions = options - buildOptions
    if len(invalidOptions) > 0:
        print("Invalid build options: {}\n".format(invalidOptions))
        print(helpNote)
        sys.exit()

    if "--nocompile" in options:
        if "--copy" in options:
            print("The options --nocompile and --copy don't work together.")
            sys.exit()
        if "--export" in options:
            print("The options --nocompile and --export don't work together.")
            sys.exit()

def main_Clean():
    print("Clean")


def _main():
    logger = TaskLogger()
    setupInfoList = getSetupInfoList()
    execute_PyPreprocess(setupInfoList, logger)
    execute_Cythonize(setupInfoList, logger)
    execute_Compile(setupInfoList, logger)
    execute_CopyAddon(logger)
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


# Copy Addon
###########################################

def execute_CopyAddon(logger):
    printHeader("Copy Addon")
    targetPath = "C:\\Users\\jacques\\AppData\\Roaming\\Blender Foundation\\Blender\\2.78\\scripts\\addons\\animation_nodes"
    changes = syncDirectories(addonDirectory, targetPath, iterRelativeAddonFiles)

    for path in changes["removed"]:
        print("Removed:", os.path.relpath(path, targetPath))
    for path in changes["updated"]:
        print("Updated:", os.path.relpath(path, targetPath))
    for path in changes["created"]:
        print("Created:", os.path.relpath(path, targetPath))

    totalChanged = sum(len(l) for l in changes.values())
    print("\nModified {} files.".format(totalChanged))

def iterRelativeAddonFiles(basepath):
    for root, dirs, files in os.walk(basepath, topdown = True):
        for directory in dirs:
            if isAddonDirectoryIgnored(directory):
                dirs.remove(directory)
        for filename in files:
            if not isAddonFileIgnored(filename):
                fullpath = os.path.join(root, filename)
                yield os.path.relpath(fullpath, basepath)

def isAddonDirectoryIgnored(name):
    return name in {".git", "__pycache__"}

def isAddonFileIgnored(name):
    extensions = [".src", ".pxd", ".pyx", ".html", ".c"]
    names = {".gitignore", "__setup_info.py"}
    return any(name.endswith(ext) for ext in extensions) or name in names

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
    print("\nSave Summary: " + os.path.basename(summaryPath))

def getSummary(logger):
    return {
        "PyPreprocess" : getPyPreprocessSummary(logger),
        "Cythonize" : getCythonizeSummary(logger),
        "Compilation" : getCompilationSummary(logger),
        "Platform" : getPlatformSummary()
    }

def getPyPreprocessSummary(logger):
    return [task.getSummary() for task in logger.pyPreprocessTasks]

def getCythonizeSummary(logger):
    return [task.getSummary() for task in logger.cythonizeTasks]

def getCompilationSummary(logger):
    return [task.getSummary() for task in logger.compilationTasks]

def getPlatformSummary():
    summary = {
        "sys.version" : sys.version,
        "sys.platform" : sys.platform,
        "sys.api_version" : sys.api_version,
        "sys.version_info" : sys.version_info,
        "os.name" : os.name
    }
    if setupOptions.cythonize:
        import Cython
        summary["Cython.__version__"] = Cython.__version__
    else:
        summary["Cython.__version__"] = "unused"
    return summary


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

def syncDirectories(source, target, relpathSelector):
    if not directoryExists(target):
        os.mkdir(target)

    existingFilesInSource = set(relpathSelector(source))
    existingFilesInTarget = set(relpathSelector(target))

    removedFiles = []
    createdFiles = []
    updatedFiles = []

    filesToRemove = existingFilesInTarget - existingFilesInSource
    for relativePath in filesToRemove:
        path = os.path.join(target, relativePath)
        removeFile(path)
        removedFiles.append(path)

    filesToCreate = existingFilesInSource - existingFilesInTarget
    for relativePath in filesToCreate:
        sourcePath = os.path.join(source, relativePath)
        targetPath = os.path.join(target, relativePath)
        copyFile(sourcePath, targetPath)
        createdFiles.append(targetPath)

    filesToUpdate = existingFilesInSource.intersection(existingFilesInTarget)
    for relativePath in filesToUpdate:
        sourcePath = os.path.join(source, relativePath)
        targetPath = os.path.join(target, relativePath)
        lastSourceModification = tryGetLastModificationTime(sourcePath)
        lastTargetModification = tryGetLastModificationTime(targetPath)
        if lastSourceModification > lastTargetModification:
            overwriteFile(sourcePath, targetPath)
            updatedFiles.append(targetPath)

    return {
        "removed" : removedFiles,
        "created" : createdFiles,
        "updated" : updatedFiles
    }


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
    extensions = setOfStrings(extension)
    for root, dirs, files in os.walk(basepath):
        for filename in files:
            _, ext = os.path.splitext(filename)
            if ext in extensions:
                yield os.path.join(root, filename)

def setOfStrings(strings):
    if isinstance(strings, str):
        return {strings}
    else:
        return set(strings)

def iterPathsWithFileName(basepath, filename):
    for root, dirs, files in os.walk(basepath):
        if filename in files:
            yield os.path.join(root, filename)

def overwriteFile(source, target):
    removeFile(target)
    copyFile(source, target)

def copyFile(source, target):
    directory = os.path.dirname(target)
    if not directoryExists(directory):
        os.makedirs(directory)
    shutil.copyfile(source, target)

def removeFile(path):
    try:
        os.remove(path)
    except:
        if tryGetFileAccessPermission(path):
            os.remove(path)

def tryGetFileAccessPermission(path):
    try:
        os.chmod(path, stat.S_IWUSR)
        return True
    except:
        return False

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
