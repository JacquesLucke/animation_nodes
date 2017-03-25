from ... utils.names import replaceVariableName

class CodeEffect:
    def apply(self, node, code):
        return code

    def iterIndented(self, code):
        yield from ("    " + line for line in code.splitlines())

class VectorizeCodeEffect(CodeEffect):
    def __init__(self):
        self.baseInputNames = []
        self.listInputNames = []
        self.newBaseInputNames = []

        self.baseOutputNames = []
        self.listOutputNames = []
        self.newBaseOutputNames = []

    def input(self, baseName, listName):
        self.baseInputNames.append(baseName)
        self.listInputNames.append(listName)
        self.newBaseInputNames.append(self.rename(baseName))

    def output(self, baseName, listName):
        self.baseOutputNames.append(baseName)
        self.listOutputNames.append(listName)
        self.newBaseOutputNames.append(self.rename(baseName))

    def rename(self, name):
        return "_base_" + name

    def apply(self, node, code):
        if len(self.baseInputNames) == 0:
            yield code
            return

        baseInputNamesString = ", ".join(self.newBaseInputNames)
        listInputNamesString = ", ".join(self.listInputNames)

        for oldName, newName in zip(self.baseInputNames + self.baseOutputNames,
                                    self.newBaseInputNames + self.newBaseOutputNames):
            code = replaceVariableName(code, oldName, newName)

        yield "for ({}, ) in zip({}):".format(baseInputNamesString, listInputNamesString)
        yield from self.iterIndented(code)
        yield "    pass"
