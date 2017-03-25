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
        self.outputIndices = []

    def input(self, baseName, listName):
        self.baseInputNames.append(baseName)
        self.listInputNames.append(listName)
        self.newBaseInputNames.append(self.rename(baseName))

    def output(self, baseName, listName, index):
        self.baseOutputNames.append(baseName)
        self.listOutputNames.append(listName)
        self.newBaseOutputNames.append(self.rename(baseName))
        self.outputIndices.append(index)

    def rename(self, name):
        return "_base_" + name

    def apply(self, node, code):
        if len(self.baseInputNames) == 0:
            yield code
            return

        for name, index in zip(self.listOutputNames, self.outputIndices):
            socket = node.outputs[index]
            if socket.isLinked and name not in self.listInputNames:
                yield "{} = self.outputs[{}].getDefaultValue()".format(name, index)

        baseInputNamesString = ", ".join(self.newBaseInputNames)
        listInputNamesString = ", ".join(self.listInputNames)

        for oldName, newName in zip(self.baseInputNames + self.baseOutputNames,
                                    self.newBaseInputNames + self.newBaseOutputNames):
            code = replaceVariableName(code, oldName, newName)

        yield "for ({}, ) in zip({}):".format(baseInputNamesString, listInputNamesString)
        yield from self.iterIndented(code)

        for baseName, listName, index in zip(self.newBaseOutputNames, self.listOutputNames, self.outputIndices):
            socket = node.outputs[index]
            if socket.isLinked and listName not in self.listInputNames:
                yield "    {}.append({})".format(listName, baseName)

        yield "    pass"
