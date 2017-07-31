class Logger:
    def __init__(self):
        self.pyPreprocessTasks = []
        self.cythonizeTasks = []
        self.compilationTasks = []
        self.generatedFiles = []

    def logPyPreprocessTask(self, task):
        self.pyPreprocessTasks.append(task)

    def logCythonizeTask(self, task):
        self.cythonizeTasks.append(task)

    def logCompilationTask(self, task):
        self.compilationTasks.append(task)

    def logGeneratedFile(self, path):
        self.generatedFiles.append(path)

    def getGeneratedFiles(self):
        paths = []
        paths.extend(task.target for task in self.getAllTasks() if task.target is not None)
        paths.extend(self.generatedFiles)
        return paths

    def getChangedFiles(self):
        paths = []
        paths.extend(task.target for task in self.getAllTasks() if task.targetChanged)
        paths.extend(self.generatedFiles)
        return paths

    def getAllTasks(self):
        return self.pyPreprocessTasks + self.cythonizeTasks + self.compilationTasks
