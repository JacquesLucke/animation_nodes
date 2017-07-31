import os
import sys
import glob
import json
from . generic import *
from . task import GenerateFileTask

def execute_Compile(setupInfoList, logger, addonDirectory):
    printHeader("Compile")
    tasks = getCompileTasks(addonDirectory)
    for i, task in enumerate(tasks, 1):
        print("{}/{}:".format(i, len(tasks)))
        logger.logCompilationTask(task)
        task.execute()

    compilationInfo = getPlatformSummary()
    compilationInfoPath = os.path.join(addonDirectory, "compilation_info.json")
    writeJsonFile(compilationInfoPath, compilationInfo)
    logger.logGeneratedFile(compilationInfoPath)

def getCompileTasks(addonDirectory):
    tasks = []
    for path in iterFilesToCompile(addonDirectory):
        tasks.append(CompileExtModuleTask(path))
    return tasks

def iterFilesToCompile(addonDirectory):
    for path in iterPathsWithExtension(addonDirectory, ".pyx"):
        yield changeFileExtension(path, ".c")


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

def getCythonMetadata(path):
    text = readLinesBetween(path, "BEGIN: Cython Metadata", "END: Cython Metadata")
    return json.loads(text)
