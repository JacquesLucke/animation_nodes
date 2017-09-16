import os
import sys
import glob
import json
from . generic import *

def execute_Compile(setupInfoList, addonDirectory):
    printHeader("Compile")
    tasks = getCompileTasks(addonDirectory)
    for i, task in enumerate(tasks, 1):
        print("{}/{}:".format(i, len(tasks)))
        task.execute()

    compilationInfo = getPlatformSummary()
    compilationInfoPath = os.path.join(addonDirectory, "compilation_info.json")
    writeJsonFile(compilationInfoPath, compilationInfo)

def getCompileTasks(addonDirectory):
    tasks = []
    for path in iterFilesToCompile(addonDirectory):
        tasks.append(CompileExtModuleTask(path))
    return tasks

def iterFilesToCompile(addonDirectory):
    for path in iterPathsWithExtension(addonDirectory, ".pyx"):
        language = getPyxTargetLanguage(path)
        if language == "c++":
            yield changeFileExtension(path, ".cpp")
        elif language == "c":
            yield changeFileExtension(path, ".c")


class CompileExtModuleTask:
    def __init__(self, path):
        self.path = path

    def execute(self):
        extension = getExtensionFromPath(self.path)
        buildExtensionInplace(extension)

def getPossibleCompiledFilesWithTime(cpath):
    directory = os.path.dirname(cpath)
    name = getFileNameWithoutExtension(cpath)
    pattern = os.path.join(directory, name) + ".*"
    paths = glob.glob(pattern + ".pyd") + glob.glob(pattern + ".so")
    return [(path, tryGetLastModificationTime(path)) for path in paths]

def getExtensionFromPath(path):
    from distutils.core import Extension
    metadata = getCythonMetadata(path)
    moduleName = metadata["module_name"]

    kwargs = {
        "sources" : [path],
        "include_dirs" : [],
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

    infoFile = changeFileExtension(path, "_setup_info.py")
    for key, values in getExtensionsArgsFromInfoFile(infoFile).items():
        kwargs[key].extend(values)

    return Extension(moduleName, **kwargs)

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

def getCythonMetadata(path):
    text = readLinesBetween(path, "BEGIN: Cython Metadata", "END: Cython Metadata")
    return json.loads(text)
