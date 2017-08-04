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
        self.inputIndices = []
        self.allowInputListExtension = []

        self.baseOutputNames = []
        self.listOutputNames = []
        self.newBaseOutputNames = []
        self.outputIndices = []

    def input(self, baseName, listName, index, allowListExtension = True):
        self.baseInputNames.append(baseName)
        self.listInputNames.append(listName)
        self.newBaseInputNames.append(self.rename(baseName))
        self.inputIndices.append(index)
        self.allowInputListExtension.append(allowListExtension)

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

        iteratorName = "vectorizeIterator"
        yield from self.iterOutputListCreationLines(node)
        yield from self.iterIteratorCreationLines(iteratorName)
        yield self.getLoopStartLine(iteratorName)
        yield from self.iterIndented(self.renameVariables(code))
        yield from self.iterAppendToOutputListLines(node)
        yield "    pass"

    def iterOutputListCreationLines(self, node):
        for name, index in zip(self.listOutputNames, self.outputIndices):
            socket = node.outputs[index]
            if socket.isLinked and name not in self.listInputNames:
                yield "{} = self.outputs[{}].getDefaultValue()".format(name, index)

    def iterIteratorCreationLines(self, iteratorName):
        if len(self.listInputNames) == 1:
            yield "{} = {}".format(iteratorName, self.listInputNames[0])
        else:
            amountName = "iterations"
            yield from self.iterGetIterationAmountLines(amountName)
            for i, name in zip(self.inputIndices, self.listInputNames):
                yield "if len({0}) == 0: {0}_iter = itertools.cycle([AN.sockets.info.getBaseDefaultValue(self.inputs[{1}].dataType)])".format(name, i)
                yield "elif len({0}) < {1}: {0}_iter = itertools.cycle({0})".format(name, amountName)
                yield "else: {0}_iter = {0}".format(name)
            yield "{} = zip({})".format(iteratorName, ", ".join(name + "_iter" for name in self.listInputNames))

    def iterGetIterationAmountLines(self, amountName):
        noExtAmount = self.allowInputListExtension.count(False)
        if noExtAmount == 0:
            lengths = ["len({})".format(name) for name in self.listInputNames]
            yield "{} = max({})".format(amountName, ", ".join(lengths))
        elif noExtAmount == 1:
            yield "{} = len({})".format(amountName, self.listInputNames[self.allowInputListExtension.index(False)])
        else:
            lengths = []
            for name, allowExtension in zip(self.listInputNames, self.allowInputListExtension):
                if not allowExtension:
                    lengths.append("len({})".format(name))
            yield "{} = min({})".format(amountName, ", ".join(lengths))


    def getLoopStartLine(self, iteratorName):
        return "for {} in {}:".format(", ".join(self.newBaseInputNames), iteratorName)

    def iterAppendToOutputListLines(self, node):
        for baseName, listName, index in zip(self.newBaseOutputNames, self.listOutputNames, self.outputIndices):
            socket = node.outputs[index]
            if socket.isLinked and listName not in self.listInputNames:
                yield "    {}.append({})".format(listName, baseName)

    def renameVariables(self, code):
        for oldName, newName in zip(self.baseInputNames + self.baseOutputNames,
                                    self.newBaseInputNames + self.newBaseOutputNames):
            code = replaceVariableName(code, oldName, newName)
        return code
