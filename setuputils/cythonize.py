from . generic import *
from . task import GenerateFileTask

def execute_Cythonize(setupInfoList, logger, addonDirectory):
    printHeader("Run Cythonize")
    tasks = getCythonizeTasks(addonDirectory)
    for i, task in enumerate(tasks, 1):
        print("{}/{}:".format(i, len(tasks)))
        logger.logCythonizeTask(task)
        task.execute()

def getCythonizeTasks(addonDirectory):
    tasks = []
    for path in iterCythonFilePaths(addonDirectory):
        tasks.append(CythonizeTask(path))
    return tasks

def iterCythonFilePaths(addonDirectory):
    yield from iterPathsWithExtension(addonDirectory, ".pyx")

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
