from . generic import *

def execute_Cythonize(setupInfoList, addonDirectory):
    printHeader("Run Cythonize")
    tasks = getCythonizeTasks(addonDirectory)
    for i, task in enumerate(tasks, 1):
        print("{}/{}:".format(i, len(tasks)))
        task.execute()

def getCythonizeTasks(addonDirectory):
    tasks = []
    for path in iterCythonFilePaths(addonDirectory):
        tasks.append(CythonizeTask(path))
    return tasks

def iterCythonFilePaths(addonDirectory):
    yield from iterPathsWithExtension(addonDirectory, ".pyx")

class CythonizeTask:
    def __init__(self, path):
        self.path = path

    def execute(self):
        from Cython.Build import cythonize
        cythonize(self.path)
