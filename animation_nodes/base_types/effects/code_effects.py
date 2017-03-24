class CodeEffect:
    def apply(self, node, code):
        return code

    def iterIndented(self, code):
        yield from ("    " + line for line in code.splitlines())
