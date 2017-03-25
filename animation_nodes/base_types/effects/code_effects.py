class CodeEffect:
    def apply(self, node, code):
        return code

    def iterIndented(self, code):
        yield from ("    " + line for line in code.splitlines())

class VectorizeCodeEffect(CodeEffect):
    def __init__(self):
        self.baseInputNames = []
        self.listInputNames = []

        self.baseOutputNames = []
        self.listOutputNames = []

    def input(self, baseName, listName):
        self.baseInputNames.append(baseName)
        self.listInputNames.append(listName)

    def output(self, baseName, listName):
        self.baseOutputNames.append(baseName)
        self.listOutputNames.append(listName)

    def apply(self, node, code):
        if len(self.baseInputNames) == 0:
            yield code
            return

        baseInputNamesString = ", ".join(self.baseInputNames)
        listInputNamesString = ", ".join(self.listInputNames)

        yield "for ({}, ) in zip({}):".format(baseInputNamesString, listInputNamesString)
        yield from self.iterIndented(code)
        yield "    pass"
