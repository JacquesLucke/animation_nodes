import os
import re
import sys
import glob
import time
from . generic import *

def execute_Compile(setupInfoList, addonDirectory):
    printHeader("Compile")
    tasks = getCompileTasks(setupInfoList, addonDirectory)
    for i, task in enumerate(tasks, 1):
        print("{}/{}:".format(i, len(tasks)))
        task.execute()

    compilationInfo = getPlatformSummary()
    compilationInfo["date"] = int(time.time())
    compilationInfoPath = os.path.join(addonDirectory, "compilation_info.json")
    writeJsonFile(compilationInfoPath, compilationInfo)

def getCompileTasks(setupInfoList, addonDirectory):
    includeDirs = list(iterCustomIncludeDirs(setupInfoList))

    tasks = []
    for path in iterFilesToCompile(addonDirectory):
        tasks.append(CompileExtModuleTask(path, addonDirectory, includeDirs))
    return tasks

def iterFilesToCompile(addonDirectory):
    for path in iterPathsWithExtension(addonDirectory, ".pyx"):
        language = getPyxTargetLanguage(path)
        if language == "c++":
            yield changeFileExtension(path, ".cpp")
        elif language == "c":
            yield changeFileExtension(path, ".c")

def iterCustomIncludeDirs(setupInfoList):
    fName = "getIncludeDirs"
    for setupInfo in setupInfoList:
        if fName in setupInfo:
            for name in setupInfo[fName]():
                yield changeFileName(setupInfo["__file__"], name)

class CompileExtModuleTask:
    def __init__(self, path, addonDirectory, includeDirs = []):
        self.path = path
        self.addonDirectory = addonDirectory
        self.includeDirs = includeDirs

    def execute(self):
        extension = getExtensionFromPath(self.path, self.addonDirectory, self.includeDirs)
        buildExtensionInplace(extension)

def getPossibleCompiledFilesWithTime(cpath):
    directory = os.path.dirname(cpath)
    name = getFileNameWithoutExtension(cpath)
    pattern = os.path.join(directory, name) + ".*"
    paths = glob.glob(pattern + ".pyd") + glob.glob(pattern + ".so")
    return [(path, tryGetLastModificationTime(path)) for path in paths]

def getExtensionFromPath(path, addonDirectory, includeDirs = []):
    from distutils.core import Extension
    moduleName = getModuleNameOfPath(path, addonDirectory)

    kwargs = {
        "sources" : [path],
        "include_dirs" : includeDirs,
        "define_macros" : [],
        "undef_macros" : [],
        "library_dirs" : [],
        "libraries" : [],
        "runtime_library_dirs" : [],
        "extra_objects" : [],
        "extra_compile_args" : [],
        "extra_link_args" : [],
        "export_symbols" : [],
        "depends" : []
    }

    for key, values in getExtensionArgsFromSetupOptions(getSetupOptions(path)).items():
        kwargs[key].extend(values)

    infoFile = changeFileExtension(path, "_setup_info.py")
    for key, values in getExtensionsArgsFromInfoFile(infoFile).items():
        kwargs[key].extend(values)

    return Extension(moduleName, **kwargs)

def getModuleNameOfPath(path, basePath):
    relativePath = os.path.relpath(os.path.splitext(path)[0], os.path.dirname(basePath))
    return ".".join(splitPath(relativePath))

def getExtensionsArgsFromInfoFile(infoFilePath):
    if not fileExists(infoFilePath):
        return {}

    data = executePythonFile(infoFilePath)
    fName = "getExtensionArgs"
    if fName not in data:
        return {}

    return data[fName](Utils)

def buildExtensionInplace(extension):
    from distutils.core import setup
    oldArgs = sys.argv
    sys.argv = [oldArgs[0], "build_ext", "--inplace"]
    setup(ext_modules = [extension])
    sys.argv = oldArgs

def getSetupOptions(path):
    pyxPath = changeFileExtension(path, ".pyx")
    if not fileExists(pyxPath):
        return set()

    options = set()
    text = readTextFile(pyxPath)
    for match in re.finditer(r"^#\s*setup\s*:\s*options\s*=(.*)$", text, flags = re.MULTILINE):
        options.update(match.group(1).split())
    return options

def getExtensionArgsFromSetupOptions(options):
    args = {}
    if "c++11" in options:
        if onLinux or onMacOS:
            args["extra_compile_args"] = ["-std=c++11"]
    return args
